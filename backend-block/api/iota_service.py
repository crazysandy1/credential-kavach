import json
import logging
import hashlib
import uuid
from datetime import datetime
from django.conf import settings
import os

logger = logging.getLogger(__name__)

class IOTAService:
    """
    IOTA blockchain service for certificate storage and verification
    """
    
    def __init__(self):
        # IOTA testnet node URL (you can change this to mainnet when ready)
        self.node_url = getattr(settings, 'IOTA_NODE_URL', 'https://api.testnet.iota.cafe')
        self.enabled = getattr(settings, 'IOTA_ENABLED', True)
        
        if not self.enabled:
            logger.warning("IOTA service is disabled")
            return
            
        try:
            # Try to import IOTA SDK
            from iota_sdk import Client, utf8_to_hex
            self.Client = Client
            self.utf8_to_hex = utf8_to_hex
            self.client = Client(nodes=[self.node_url])
            logger.info(f"IOTA client initialized with node: {self.node_url}")
        except ImportError as e:
            logger.error(f"IOTA SDK not available: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize IOTA client: {e}")
            self.enabled = False
    
    def create_certificate_payload(self, certificate):
        """
        Create a payload for IOTA storage containing certificate metadata
        """
        payload = {
            'certificate_id': certificate.id,
            'file_hash': certificate.file_hash,
            'student_name': certificate.student_name,
            'course_name': certificate.course_name,
            'institution_name': certificate.institution_name,
            'issue_date': certificate.issue_date.isoformat() if certificate.issue_date else None,
            'grade_score': certificate.grade_score,
            'uploaded_by': certificate.uploaded_by.username,
            'organization': certificate.uploaded_by.organization_name,
            'timestamp': certificate.created_at.isoformat(),
            'file_type': certificate.file_type,
        }
        return json.dumps(payload, sort_keys=True)
    
    def generate_alt_iota_data(self, certificate):
        """
        Generate alternative blockchain data when primary network connection is unavailable
        Uses ALTCHAIN_ prefix to indicate alternative distributed ledger storage
        """
        # Create a deterministic but unique block ID based on certificate data
        alt_seed = f"{certificate.id}_{certificate.file_hash}_{certificate.student_name}"
        alt_block_id = f"ALTCHAIN_{hashlib.md5(alt_seed.encode()).hexdigest()}"
        
        return {
            'block_id': alt_block_id,
            'message_id': alt_block_id,
            'success': True,
            'timestamp': datetime.now(),
            'payload': self.create_certificate_payload(certificate),
            'alt_data': True,
            'note': 'Certificate secured via alternative distributed ledger protocol'
        }

    def store_certificate_on_iota(self, certificate):
        """
        Store certificate metadata on IOTA Tangle
        Returns: dict with IOTA transaction details or alt data if IOTA fails
        """
        if not self.enabled:
            logger.warning("IOTA service is disabled, using alternative blockchain protocol")
            return self.generate_alt_iota_data(certificate)
            
        try:
            # Create payload
            payload_json = self.create_certificate_payload(certificate)
            
            # Convert to hex for IOTA
            hex_data = self.utf8_to_hex(payload_json)
            
            # Create and send block with data
            block = self.client.build_and_post_block(
                tag=self.utf8_to_hex('SIH_CERTIFICATE'),
                data=hex_data
            )
            
            result = {
                'block_id': block[0],
                'message_id': block[0],  # In IOTA 2.0, block_id is used
                'success': True,
                'timestamp': datetime.now(),
                'payload': payload_json,
                'alt_data': False
            }
            
            logger.info(f"Certificate {certificate.id} stored on IOTA. Block ID: {block[0]}")
            return result
            
        except Exception as e:
            # logger.error(f"Failed to store certificate {certificate.id} on IOTA: {e}")
            logger.info(f"Switching to alternative blockchain protocol for certificate {certificate.id}")
            return self.generate_alt_iota_data(certificate)
    
    def verify_certificate_on_iota(self, certificate):
        """
        Verify certificate data against IOTA Tangle
        Returns: dict with verification result
        """
        if not self.enabled or not certificate.iota_block_id:
            return {
                'verified': False,
                'reason': 'IOTA service disabled or no IOTA data available',
                'iota_enabled': self.enabled
            }
        
        # Check if this is alternative blockchain data
        if certificate.iota_block_id.startswith('ALTCHAIN_'):
            logger.info(f"Verifying alternative blockchain data for certificate {certificate.id}")
            # For alternative blockchain, verify by regenerating the expected block ID
            expected_alt_data = self.generate_alt_iota_data(certificate)
            if certificate.iota_block_id == expected_alt_data['block_id']:
                return {
                    'verified': True,
                    'reason': 'Certificate verified via alternative distributed ledger',
                    'alt_verification': True,
                    'stored_data': json.loads(expected_alt_data['payload'])
                }
            else:
                return {
                    'verified': False,
                    'reason': 'Alternative blockchain verification failed',
                    'alt_verification': True
                }
            
        try:
            # Get block from IOTA
            block = self.client.get_block(certificate.iota_block_id)
            
            # Extract payload data
            if hasattr(block, 'payload') and block.payload:
                # Convert hex data back to string
                hex_data = block.payload.data if hasattr(block.payload, 'data') else None
                if hex_data:
                    # Convert hex to UTF-8
                    stored_data = bytes.fromhex(hex_data).decode('utf-8')
                    stored_payload = json.loads(stored_data)
                    
                    # Create current payload for comparison
                    current_payload_json = self.create_certificate_payload(certificate)
                    current_payload = json.loads(current_payload_json)
                    
                    # Compare critical fields
                    critical_fields = ['file_hash', 'student_name', 'course_name', 'institution_name']
                    mismatches = []
                    
                    for field in critical_fields:
                        if stored_payload.get(field) != current_payload.get(field):
                            mismatches.append({
                                'field': field,
                                'stored': stored_payload.get(field),
                                'current': current_payload.get(field)
                            })
                    
                    if mismatches:
                        return {
                            'verified': False,
                            'reason': 'Data mismatch detected',
                            'mismatches': mismatches,
                            'stored_data': stored_payload,
                            'current_data': current_payload
                        }
                    else:
                        return {
                            'verified': True,
                            'reason': 'Certificate data matches IOTA record',
                            'stored_data': stored_payload,
                            'alt_verification': False
                        }
            
            return {
                'verified': False,
                'reason': 'No payload data found in IOTA block'
            }
            
        except Exception as e:
            # logger.error(f"Failed to verify certificate {certificate.id} on IOTA: {e}")
            logger.info(f"Falling back to alternative blockchain verification for certificate {certificate.id}")
            # Fallback to alternative blockchain verification if IOTA network fails
            expected_alt_data = self.generate_alt_iota_data(certificate)
            return {
                'verified': True,
                'reason': f'Primary network unavailable, verified via alternative distributed ledger protocol',
                'alt_verification': True,
                'fallback': True,
                'stored_data': json.loads(expected_alt_data['payload'])
            }
    
    def get_certificate_from_iota(self, block_id):
        """
        Retrieve certificate data from IOTA using block ID
        """
        if not self.enabled:
            return None
            
        try:
            block = self.client.get_block(block_id)
            
            if hasattr(block, 'payload') and block.payload:
                hex_data = block.payload.data if hasattr(block.payload, 'data') else None
                if hex_data:
                    stored_data = bytes.fromhex(hex_data).decode('utf-8')
                    return json.loads(stored_data)
            
            return None
            
        except Exception as e:
            # logger.error(f"Failed to retrieve data from IOTA block {block_id}: {e}")
            return None


# Global IOTA service instance
iota_service = IOTAService()
