extends SceneTree

class OneShotPickup:
    var consumed := false

    func collect() -> bool:
        if consumed:
            return false
        consumed = true
        return true

func _initialize() -> void:
    var pickup := OneShotPickup.new()
    assert(pickup.collect(), "first collection should succeed")
    assert(not pickup.collect(), "second collection should fail")
    assert(pickup.consumed, "pickup should be consumed")
    print("PASS first=true second=false consumed=true")
    quit(0)
