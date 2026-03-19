import hashlib
import hmac

def generate_signature(raw_value_str: str, key: str, iterations: int) -> str:
    """
    Generates a PBKDF2 HMAC SHA-256 signature for the given value.
    Treats the secret key as the password and the raw value as the salt.
    """
    password_bytes = key.encode('utf-8')
    salt_bytes = raw_value_str.encode('utf-8')

    # Generate the hash
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name='sha256', 
        password=password_bytes, 
        salt=salt_bytes, 
        iterations=iterations
    )
    return hash_bytes.hex()

# ye signature validate kr ke deta 
def validate_signature(hash_val: str, sensor_data: str, key: str, iterations: int) -> bool:
    sig = generate_signature(sensor_data, key, iterations)

    return hmac.compare_digest(sig, hash_val)



