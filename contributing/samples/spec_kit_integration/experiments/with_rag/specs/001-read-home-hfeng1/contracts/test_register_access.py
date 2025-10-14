"""
Contract tests for watchdog timer register access.
These tests should fail initially as there is no implementation yet.
"""

import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1/wdt"

def test_wdogload_read_write():
    """Test reading and writing the WDOGLOAD register"""
    # Test reading initial value
    response = requests.get(f"{BASE_URL}/registers/WDOGLOAD")
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert 0 <= data["value"] <= 0xFFFFFFFF
    
    # Test writing a new value
    new_value = 0x12345678
    response = requests.put(f"{BASE_URL}/registers/WDOGLOAD", 
                          json={"value": new_value})
    assert response.status_code == 200
    
    # Verify the value was set
    response = requests.get(f"{BASE_URL}/registers/WDOGLOAD")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == new_value

def test_wdogvalue_read_only():
    """Test that WDOGVALUE is read-only"""
    # Read current value
    response = requests.get(f"{BASE_URL}/registers/WDOGVALUE")
    assert response.status_code == 200
    initial_value = response.json()["value"]
    
    # Attempt to write (should fail)
    response = requests.put(f"{BASE_URL}/registers/WDOGVALUE",
                          json={"value": 0x12345678})
    assert response.status_code == 405  # Method not allowed

def test_wdogcontrol_read_write():
    """Test reading and writing the WDOGCONTROL register"""
    # Test reading initial value
    response = requests.get(f"{BASE_URL}/registers/WDOGCONTROL")
    assert response.status_code == 200
    data = response.json()
    assert "int_en" in data
    assert "res_en" in data
    assert isinstance(data["int_en"], bool)
    assert isinstance(data["res_en"], bool)
    
    # Test writing new values
    response = requests.put(f"{BASE_URL}/registers/WDOGCONTROL",
                          json={"int_en": True, "res_en": False})
    assert response.status_code == 200
    
    # Verify the values were set
    response = requests.get(f"{BASE_URL}/registers/WDOGCONTROL")
    assert response.status_code == 200
    data = response.json()
    assert data["int_en"] == True
    assert data["res_en"] == False

def test_wdogintclr_write_only():
    """Test that WDOGINTCLR is write-only"""
    # Attempt to read (should fail)
    response = requests.get(f"{BASE_URL}/registers/WDOGINTCLR")
    assert response.status_code == 405  # Method not allowed
    
    # Write to clear interrupt
    response = requests.put(f"{BASE_URL}/registers/WDOGINTCLR",
                          json={"clear": True})
    assert response.status_code == 200

def test_wdogris_read_only():
    """Test that WDOGRIS is read-only"""
    # Read current value
    response = requests.get(f"{BASE_URL}/registers/WDOGRIS")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert isinstance(data["status"], bool)
    
    # Attempt to write (should fail)
    response = requests.put(f"{BASE_URL}/registers/WDOGRIS",
                          json={"status": True})
    assert response.status_code == 405  # Method not allowed

def test_wdogmis_read_only():
    """Test that WDOGMIS is read-only"""
    # Read current value
    response = requests.get(f"{BASE_URL}/registers/WDOGMIS")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert isinstance(data["status"], bool)
    
    # Attempt to write (should fail)
    response = requests.put(f"{BASE_URL}/registers/WDOGMIS",
                          json={"status": True})
    assert response.status_code == 405  # Method not allowed

def test_wdoglock_read_write():
    """Test reading and writing the WDOGLOCK register"""
    # Test reading initial state (should be locked)
    response = requests.get(f"{BASE_URL}/registers/WDOGLOCK")
    assert response.status_code == 200
    data = response.json()
    assert "locked" in data
    # Initial state may vary depending on implementation
    
    # Test unlocking
    unlock_key = 0x1ACCE551
    response = requests.put(f"{BASE_URL}/registers/WDOGLOCK",
                          json={"unlock_key": unlock_key})
    assert response.status_code == 200
    
    # Verify unlocked state
    response = requests.get(f"{BASE_URL}/registers/WDOGLOCK")
    assert response.status_code == 200
    data = response.json()
    assert data["locked"] == False
    
    # Test locking again
    response = requests.put(f"{BASE_URL}/registers/WDOGLOCK",
                          json={"unlock_key": 0x00000000})
    assert response.status_code == 200

def test_register_protection():
    """Test that registers are protected when locked"""
    # Lock the registers
    response = requests.put(f"{BASE_URL}/registers/WDOGLOCK",
                          json={"unlock_key": 0x00000000})
    assert response.status_code == 200
    
    # Try to write to a protected register (should fail)
    response = requests.put(f"{BASE_URL}/registers/WDOGLOAD",
                          json={"value": 0x12345678})
    assert response.status_code == 403  # Forbidden

def test_wdogitcr_read_write():
    """Test reading and writing the WDOGITCR register"""
    # Test reading initial value
    response = requests.get(f"{BASE_URL}/registers/WDOGITCR")
    assert response.status_code == 200
    data = response.json()
    assert "test_mode" in data
    assert isinstance(data["test_mode"], bool)
    
    # Test enabling test mode
    response = requests.put(f"{BASE_URL}/registers/WDOGITCR",
                          json={"test_mode": True})
    assert response.status_code == 200
    
    # Verify test mode enabled
    response = requests.get(f"{BASE_URL}/registers/WDOGITCR")
    assert response.status_code == 200
    data = response.json()
    assert data["test_mode"] == True

def test_wdogitop_write_only():
    """Test that WDOGITOP is write-only"""
    # Attempt to read (should fail)
    response = requests.get(f"{BASE_URL}/registers/WDOGITOP")
    assert response.status_code == 405  # Method not allowed
    
    # Write test outputs
    response = requests.put(f"{BASE_URL}/registers/WDOGITOP",
                          json={"int_output": True, "res_output": False})
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])