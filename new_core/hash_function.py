import hashlib
import hmac
# SECRET_KEY = "sda_spring_2026_secure_key"
# ITERATIONS = 100000
# raw_value = sensor data rounded to two decimal places

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



def validate_signature(hash_val: str, sensor_data: str, key: str, iterations: int) -> bool:
    sig = generate_signature(sensor_data, key, iterations)

    return hmac.compare_digest(sig, hash_val)


# NOTE: TESTING
# if __name__ == "__main__":
#     hash_value = "18d9d277ba10acd37fc5f4ab791829b0b3de8c4625f75563b808f545874e2fed"
#     raw_val = str(24.99)
#     print(validate_signature(hash_value, raw_val, SECRET_KEY, ITERATIONS))



