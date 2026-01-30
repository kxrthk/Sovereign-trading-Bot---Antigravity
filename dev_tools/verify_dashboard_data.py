from memory_manager import MemoryManager

def populate_test_data():
    mm = MemoryManager()
    print(f"Current Memory: {mm.memory}")
    
    # Inject test confidence
    test_conf = 0.88 # 88%
    mm.update_oracle_confidence(test_conf)
    print(f"Updated Memory with Confidence {test_conf}")
    
    # Verify persistence
    mm2 = MemoryManager()
    saved_conf = mm2.memory.get("latest_oracle_confidence")
    print(f"Read back Confidence: {saved_conf}")
    
    assert saved_conf == test_conf
    print("Verification Successful: Memory Manager handles Oracle Confidence.")

if __name__ == "__main__":
    populate_test_data()
