extends SceneTree
# r79-scout scratch probe — PhysicsServer2D tier + interior-window cells (read-only).
# One arm per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://phys2d_events.gd -- --arm=<name>
# Prints R79 diagnostic lines and one final `PASS phys2d_events <arm> ...` line.
# No object ids / addresses / RIDs are printed (byte-stability).
# The `match arm:` dispatch in _run is the sole arm index (23 arms).

const FLOOR_A_Y := 20.0
const FLOOR_B_Y := 220.0
const FALLER_Y := -4.0

class Hook extends Node2D:
    var cb: Callable
    var fired := false

    func _physics_process(_delta: float) -> void:
        if fired:
            return
        fired = true
        cb.call()

var arm := ""
var _rb_kind := ""
var _area_kind := ""
var _faller: RigidBody2D
var _floor_a: StaticBody2D
var _area: Area2D
var _entries: Array = []
var _exits: Array = []
var _in_cb: Dictionary = {}
var _rb_cb_done := false
var _area_entries := 0
var _area_exits := 0
var _area_in_cb: Dictionary = {}
var _area_cb_done := false
var _raw_rids: Array = []
var _frame_no := 0
var _exit_frames: Array = []

func _track(rid: RID) -> RID:
    _raw_rids.append(rid)
    return rid

func _free_tracked() -> void:
    for i in range(_raw_rids.size() - 1, -1, -1):
        PhysicsServer2D.free_rid(_raw_rids[i])
    _raw_rids.clear()

func _initialize() -> void:
    for a in OS.get_cmdline_user_args():
        if a.begins_with("--arm="):
            arm = a.substr(6)
    call_deferred("_run")

func _run() -> void:
    print("R79 arm=%s godot=%s engine2d=%s separate_thread=%s" % [
        arm, Engine.get_version_info().string,
        ProjectSettings.get_setting("physics/2d/physics_engine"),
        ProjectSettings.get_setting("physics/2d/run_on_separate_thread")])
    match arm:
        "edge_srv":
            await _arm_edge_srv()
        "edge_node_srv":
            await _arm_edge_node_srv()
        "edge_node":
            await _arm_edge_node()
        "edge_revert":
            await _arm_edge_revert()
        "area_edge":
            await _arm_area_edge()
        "cm_on", "cm_off", "cm_max0", "cm_toggle_cb", "cm_deferred_cb", "cm_max0_cb":
            await _arm_cm(arm.substr(3))
        "rb_srv_set_state", "rb_node_position", "rb_queue_free", "rb_free_rid", "rb_dss_in_cb":
            await _arm_rb(arm.substr(3))
        "area_monitoring_direct", "area_monitoring_deferred", "area_free_rid", "area_queue_free", "area_srv_set_state", "area_node_position", "area_dss_in_cb":
            await _arm_area(arm.substr(5))
        _:
            _fail("unknown_arm")

func _fail(reason: String) -> void:
    print("FAIL phys2d_events %s reason=%s" % [arm, reason])
    quit(1)

func _finish(line: String) -> void:
    _free_tracked()
    print("PASS phys2d_events " + line)
    quit(0)

func _space() -> RID:
    return root.world_2d.space

func _frames(n: int) -> void:
    for i in n:
        await physics_frame
        _frame_no += 1

func _wait_for(cond: Callable, max_frames: int) -> int:
    for i in max_frames:
        if cond.call():
            return i
        await physics_frame
        _frame_no += 1
    return -1

func _mk_static(pos: Vector2, size: Vector2, nm: String) -> StaticBody2D:
    var b := StaticBody2D.new()
    b.name = nm
    var cs := CollisionShape2D.new()
    var rs := RectangleShape2D.new()
    rs.size = size
    cs.shape = rs
    b.add_child(cs)
    b.position = pos
    root.add_child(b)
    return b

func _mk_faller(pos: Vector2, monitor: bool, max_contacts: int) -> RigidBody2D:
    var b := RigidBody2D.new()
    b.name = "Faller"
    var cs := CollisionShape2D.new()
    var rs := RectangleShape2D.new()
    rs.size = Vector2(10, 10)
    cs.shape = rs
    b.add_child(cs)
    b.position = pos
    b.gravity_scale = 4.0
    root.add_child(b)
    b.contact_monitor = monitor
    b.max_contacts_reported = max_contacts
    return b

func _mk_hook(cb: Callable) -> Hook:
    var h := Hook.new()
    h.cb = cb
    return h

func _q_count(at: Vector2, areas: bool) -> int:
    var dss: Variant = PhysicsServer2D.space_get_direct_state(_space())
    if dss == null:
        return -1
    var q := PhysicsPointQueryParameters2D.new()
    q.position = at
    q.collide_with_bodies = not areas
    q.collide_with_areas = areas
    return (dss as PhysicsDirectSpaceState2D).intersect_point(q).size()

func _srv_origin(rid: RID) -> Variant:
    var t: Variant = PhysicsServer2D.body_get_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM)
    if t == null:
        return "<null>"
    return (t as Transform2D).origin

func _area_srv_origin(rid: RID) -> Variant:
    var t: Variant = PhysicsServer2D.area_get_transform(rid)
    if t == null:
        return "<null>"
    return (t as Transform2D).origin

# ---------------------------------------------------------------- tier arms
func _arm_edge_srv() -> void:
    var raw := _track(PhysicsServer2D.body_create())
    PhysicsServer2D.body_set_mode(raw, PhysicsServer2D.BODY_MODE_STATIC)
    var shape := _track(PhysicsServer2D.rectangle_shape_create())
    PhysicsServer2D.shape_set_data(shape, Vector2(20, 20))
    PhysicsServer2D.body_add_shape(raw, shape)
    PhysicsServer2D.body_set_space(raw, _space())
    PhysicsServer2D.body_set_state(raw, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(100, 0)))
    await _frames(2)
    var res := {}
    var hook := _mk_hook(func() -> void:
        res["q_before"] = _q_count(Vector2(100, 0), false)
        res["srv_before"] = _srv_origin(raw)
        PhysicsServer2D.body_set_state(raw, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(200, 0)))
        res["srv_after"] = _srv_origin(raw)
        res["q_new"] = _q_count(Vector2(200, 0), false)
        res["q_old"] = _q_count(Vector2(100, 0), false))
    root.add_child(hook)
    await _frames(3)
    res["q_new_n1"] = _q_count(Vector2(200, 0), false)
    res["q_old_n1"] = _q_count(Vector2(100, 0), false)
    _finish("edge_srv q_before=%s srv_before=%s srv_after=%s q_new=%s q_old=%s q_new_n1=%s q_old_n1=%s" % [
        res["q_before"], res["srv_before"], res["srv_after"], res["q_new"], res["q_old"],
        res["q_new_n1"], res["q_old_n1"]])

func _arm_edge_node_srv() -> void:
    var nb := _mk_static(Vector2(300, 0), Vector2(20, 20), "NodeWall")
    await _frames(2)
    var res := {}
    var hook := _mk_hook(func() -> void:
        res["q_before"] = _q_count(Vector2(300, 0), false)
        var rid := nb.get_rid()
        PhysicsServer2D.body_set_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(200, 0)))
        res["srv_after"] = _srv_origin(rid)
        res["q_new"] = _q_count(Vector2(200, 0), false)
        res["q_old"] = _q_count(Vector2(300, 0), false)
        res["node_prop_in_cb"] = nb.position)
    root.add_child(hook)
    await _frames(3)
    res["srv_n1"] = _srv_origin(nb.get_rid())
    res["node_prop_n1"] = nb.position
    res["q_new_n1"] = _q_count(Vector2(200, 0), false)
    res["q_old_n1"] = _q_count(Vector2(300, 0), false)
    _finish("edge_node_srv q_before=%s srv_after=%s q_new=%s q_old=%s node_prop_in_cb=%s srv_n1=%s node_prop_n1=%s q_new_n1=%s q_old_n1=%s" % [
        res["q_before"], res["srv_after"], res["q_new"], res["q_old"], res["node_prop_in_cb"],
        res["srv_n1"], res["node_prop_n1"], res["q_new_n1"], res["q_old_n1"]])

func _arm_edge_node() -> void:
    var nb := _mk_static(Vector2(300, 0), Vector2(20, 20), "NodeWall")
    await _frames(2)
    var res := {}
    var hook := _mk_hook(func() -> void:
        var rid := nb.get_rid()
        nb.position = Vector2(400, 0)
        res["node_prop_in_cb"] = nb.position
        res["srv_in_cb"] = _srv_origin(rid)
        res["q_new"] = _q_count(Vector2(400, 0), false)
        res["q_old"] = _q_count(Vector2(300, 0), false))
    root.add_child(hook)
    await _frames(3)
    res["srv_n1"] = _srv_origin(nb.get_rid())
    res["q_new_n1"] = _q_count(Vector2(400, 0), false)
    res["q_old_n1"] = _q_count(Vector2(300, 0), false)
    _finish("edge_node node_prop_in_cb=%s srv_in_cb=%s q_new=%s q_old=%s srv_n1=%s q_new_n1=%s q_old_n1=%s" % [
        res["node_prop_in_cb"], res["srv_in_cb"], res["q_new"], res["q_old"],
        res["srv_n1"], res["q_new_n1"], res["q_old_n1"]])

func _arm_edge_revert() -> void:
    var nb := _mk_static(Vector2(300, 0), Vector2(20, 20), "NodeWall")
    await _frames(2)
    var res := {}
    var hook := _mk_hook(func() -> void:
        var rid := nb.get_rid()
        PhysicsServer2D.body_set_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(200, 0)))
        res["q_srv_w0"] = _q_count(Vector2(200, 0), false)
        nb.position = Vector2(400, 0)
        res["srv_after_node_w0"] = _srv_origin(rid)
        res["q_srv_after_node_w0"] = _q_count(Vector2(200, 0), false)
        res["q_node_after_node_w0"] = _q_count(Vector2(400, 0), false))
    root.add_child(hook)
    await _frames(3)
    res["srv_n1"] = _srv_origin(nb.get_rid())
    res["q_srv_n1"] = _q_count(Vector2(200, 0), false)
    res["q_node_n1"] = _q_count(Vector2(400, 0), false)
    res["node_prop_n1"] = nb.position
    _finish("edge_revert q_srv_w0=%s srv_after_node_w0=%s q_srv_after_node_w0=%s q_node_after_node_w0=%s srv_n1=%s q_srv_n1=%s q_node_n1=%s node_prop_n1=%s" % [
        res["q_srv_w0"], res["srv_after_node_w0"], res["q_srv_after_node_w0"],
        res["q_node_after_node_w0"], res["srv_n1"], res["q_srv_n1"], res["q_node_n1"],
        res["node_prop_n1"]])

func _arm_area_edge() -> void:
    var area := Area2D.new()
    area.name = "ProbeArea"
    var cs := CollisionShape2D.new()
    var rs := RectangleShape2D.new()
    rs.size = Vector2(20, 20)
    cs.shape = rs
    area.add_child(cs)
    area.position = Vector2(0, 0)
    root.add_child(area)
    await _frames(2)
    var res := {}
    var hook := _mk_hook(func() -> void:
        var rid := area.get_rid()
        res["q_before"] = _q_count(Vector2(0, 0), true)
        area.position = Vector2(100, 0)
        res["node_prop_in_cb"] = area.position
        res["srv_in_cb"] = _area_srv_origin(rid)
        res["q_new"] = _q_count(Vector2(100, 0), true)
        res["q_old"] = _q_count(Vector2(0, 0), true))
    root.add_child(hook)
    await _frames(2)
    res["srv_n1"] = _area_srv_origin(area.get_rid())
    res["q_new_n1"] = _q_count(Vector2(100, 0), true)
    res["q_old_n1"] = _q_count(Vector2(0, 0), true)
    res["node_prop_n1"] = area.position
    # direct server write: edge-0 for the query tier, node property never follows
    var hook2 := _mk_hook(func() -> void:
        PhysicsServer2D.area_set_transform(area.get_rid(), Transform2D(0, Vector2(200, 0)))
        res["srv_direct_in_cb"] = _area_srv_origin(area.get_rid())
        res["q_direct"] = _q_count(Vector2(200, 0), true)
        res["node_prop_direct_in_cb"] = area.position)
    root.add_child(hook2)
    await _frames(2)
    res["srv_direct_n2"] = _area_srv_origin(area.get_rid())
    res["node_prop_direct_n2"] = area.position
    _finish("area_edge q_before=%s node_prop_in_cb=%s srv_in_cb=%s q_new=%s q_old=%s srv_n1=%s q_new_n1=%s q_old_n1=%s node_prop_n1=%s srv_direct_in_cb=%s q_direct=%s node_prop_direct_in_cb=%s srv_direct_n2=%s node_prop_direct_n2=%s" % [
        res["q_before"], res["node_prop_in_cb"], res["srv_in_cb"], res["q_new"], res["q_old"],
        res["srv_n1"], res["q_new_n1"], res["q_old_n1"], res["node_prop_n1"],
        res["srv_direct_in_cb"], res["q_direct"], res["node_prop_direct_in_cb"],
        res["srv_direct_n2"], res["node_prop_direct_n2"]])

# ---------------------------------------------------------------- contact_monitor arms
func _on_rb_entered(other: Node) -> void:
    _entries.append(other.get_class())
    if _rb_cb_done:
        return
    _rb_cb_done = true
    _in_cb["count"] = _faller.get_contact_count()
    _in_cb["colliders"] = _faller.get_colliding_bodies().size()
    _in_cb["monitor"] = _faller.contact_monitor
    _in_cb["max"] = _faller.max_contacts_reported
    match _rb_kind:
        "srv_set_state":
            var rid := _faller.get_rid()
            var before := _faller.global_position
            PhysicsServer2D.body_set_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(500, 500)))
            _in_cb["srv_read"] = _srv_origin(rid)
            _in_cb["node_unchanged"] = _faller.global_position == before
        "node_position":
            var rid2 := _faller.get_rid()
            _in_cb["srv_before"] = _srv_origin(rid2)
            _faller.global_position = Vector2(600, 600)
            _in_cb["node_read"] = _faller.global_position
        "queue_free":
            _faller.queue_free()
            _in_cb["queued"] = true
        "free_rid":
            PhysicsServer2D.free_rid(_faller.get_rid())
            _in_cb["freed"] = true
        "dss_in_cb":
            var dss: Variant = PhysicsServer2D.space_get_direct_state(_space())
            _in_cb["dss_null"] = dss == null
            _in_cb["q_hits"] = _q_count(Vector2(0, FLOOR_A_Y), false)
        "cm_false":
            _faller.contact_monitor = false
            _in_cb["readback"] = _faller.contact_monitor
        "cm_deferred":
            _faller.set_deferred("contact_monitor", false)
            _in_cb["readback"] = _faller.contact_monitor
        "cm_max0":
            _faller.max_contacts_reported = 0
            _in_cb["readback"] = _faller.max_contacts_reported

func _on_rb_exited(other: Node) -> void:
    _exits.append(other.get_class())
    _exit_frames.append(_frame_no)

func _arm_cm(kind: String) -> void:
    var monitor := kind != "off"
    var max_contacts := 0 if kind == "max0" else 4
    match kind:
        "toggle_cb":
            _rb_kind = "cm_false"
        "deferred_cb":
            _rb_kind = "cm_deferred"
        "max0_cb":
            _rb_kind = "cm_max0"
    _floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
    _mk_static(Vector2(0, FLOOR_B_Y), Vector2(400, 40), "FloorB")
    _faller = _mk_faller(Vector2(0, FALLER_Y), monitor, max_contacts)
    _faller.body_entered.connect(_on_rb_entered)
    _faller.body_exited.connect(_on_rb_exited)
    var entry1 := await _wait_for(func() -> bool: return _entries.size() >= 1, 20)
    var in_cb := _in_cb.duplicate()
    await _frames(6)
    _floor_a.position = Vector2(10000, 10000)
    var entry2 := await _wait_for(func() -> bool: return _entries.size() >= 2, 45)
    await _frames(2)
    var line := "cm_%s entered=%d exited=%d entry1_frame=%d entry2_frame=%d cb_fired=%s" % [
        kind, _entries.size(), _exits.size(), entry1, entry2, _rb_cb_done]
    line += " cb_count=%s cb_colliders=%s cb_monitor=%s cb_max=%s" % [
        in_cb.get("count", "-"), in_cb.get("colliders", "-"),
        in_cb.get("monitor", "-"), in_cb.get("max", "-")]
    if kind == "toggle_cb" or kind == "deferred_cb":
        line += " cb_readback=%s post_monitor=%s" % [
            in_cb.get("readback", "-"), _faller.contact_monitor]
    if kind == "max0_cb":
        line += " cb_readback=%s post_max=%s" % [
            in_cb.get("readback", "-"), _faller.max_contacts_reported]
    if kind == "toggle_cb":
        line += " post_count=%s" % _faller.get_contact_count()
    line += " valid=%s" % is_instance_valid(_faller)
    line += " exit1_frame=%s" % (_exit_frames[0] if _exit_frames.size() > 0 else -1)
    _finish(line)

# ---------------------------------------------------------------- RigidBody2D interior window
func _arm_rb(kind: String) -> void:
    _rb_kind = kind
    _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
    _faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
    _faller.body_entered.connect(_on_rb_entered)
    var entry1 := await _wait_for(func() -> bool: return _rb_cb_done, 20)
    var in_cb := _in_cb.duplicate()
    await _frames(1)
    var next_node: Variant = "<dead>"
    var next_srv: Variant = "<dead>"
    var stuck := false
    var follows := false
    if is_instance_valid(_faller):
        var p := _faller.global_position
        next_node = p
        next_srv = _srv_origin(_faller.get_rid())
        if kind == "node_position":
            stuck = absf(p.x - 600.0) < 0.01 and absf(p.y - 600.0) < 0.01
        if kind == "srv_set_state":
            follows = absf(p.x - 500.0) < 0.01
    await _frames(4)
    var late_node: Variant = "<dead>"
    if is_instance_valid(_faller):
        late_node = _faller.global_position
    var valid_after := is_instance_valid(_faller)
    var line := "rb_%s entry1_frame=%d cb_count=%s cb_colliders=%s" % [
        kind, entry1, in_cb.get("count", "-"), in_cb.get("colliders", "-")]
    line += " cb_srv_read=%s cb_node_unchanged=%s cb_node_read=%s cb_srv_before=%s" % [
        in_cb.get("srv_read", "-"), in_cb.get("node_unchanged", "-"),
        in_cb.get("node_read", "-"), in_cb.get("srv_before", "-")]
    line += " next_node=%s next_srv=%s late_node=%s node_write_stuck=%s node_follows_srv=%s valid_after=%s" % [
        next_node, next_srv, late_node, stuck, follows, valid_after]
    if kind == "queue_free":
        line += " cb_queued=%s" % in_cb.get("queued", "-")
    if kind == "free_rid":
        line += " cb_freed=%s" % in_cb.get("freed", "-")
    if kind == "dss_in_cb":
        line += " cb_dss_null=%s cb_q_hits=%s" % [
            in_cb.get("dss_null", "-"), in_cb.get("q_hits", "-")]
    _finish(line)

# ---------------------------------------------------------------- Area2D interior window
func _on_area_entered(other: Node) -> void:
    _area_entries += 1
    if _area_cb_done:
        return
    _area_cb_done = true
    _area_in_cb["cls"] = other.get_class()
    _area_in_cb["monitoring"] = _area.monitoring
    var body := other as RigidBody2D
    match _area_kind:
        "monitoring_direct":
            _area.monitoring = false
            _area_in_cb["readback"] = _area.monitoring
        "monitoring_deferred":
            _area.set_deferred("monitoring", false)
            _area_in_cb["readback"] = _area.monitoring
        "free_rid":
            PhysicsServer2D.free_rid(body.get_rid())
            _area_in_cb["freed"] = true
        "queue_free":
            other.queue_free()
            _area_in_cb["queued"] = true
        "srv_set_state":
            var rid := body.get_rid()
            _area_in_cb["srv_before"] = _srv_origin(rid)
            PhysicsServer2D.body_set_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(500, 500)))
            _area_in_cb["srv_read"] = _srv_origin(rid)
        "node_position":
            body.global_position = Vector2(600, 600)
            _area_in_cb["node_read"] = body.global_position
        "dss_in_cb":
            var dss: Variant = PhysicsServer2D.space_get_direct_state(_space())
            _area_in_cb["dss_null"] = dss == null
            _area_in_cb["q_hits"] = _q_count(Vector2(0, 0), true)

func _on_area_exited(_other: Node) -> void:
    _area_exits += 1

func _arm_area(kind: String) -> void:
    _area_kind = kind
    _area = Area2D.new()
    _area.name = "ProbeArea"
    var cs := CollisionShape2D.new()
    var rs := RectangleShape2D.new()
    rs.size = Vector2(200, 200)
    cs.shape = rs
    _area.add_child(cs)
    _area.position = Vector2(0, 0)
    root.add_child(_area)
    _area.body_entered.connect(_on_area_entered)
    _area.body_exited.connect(_on_area_exited)
    _faller = _mk_faller(Vector2(0, FALLER_Y), false, 0)
    var entry1 := await _wait_for(func() -> bool: return _area_cb_done, 20)
    var in_cb := _area_in_cb.duplicate()
    await _frames(1)
    var next_node: Variant = "<dead>"
    var next_srv: Variant = "<dead>"
    var stuck := false
    var follows := false
    if is_instance_valid(_faller):
        var p := _faller.global_position
        next_node = p
        next_srv = _srv_origin(_faller.get_rid())
        if kind == "node_position":
            stuck = absf(p.x - 600.0) < 0.01 and absf(p.y - 600.0) < 0.01
        if kind == "srv_set_state":
            follows = absf(p.x - 500.0) < 0.01
    await _frames(4)
    var late_node: Variant = "<dead>"
    if is_instance_valid(_faller):
        late_node = _faller.global_position
    var valid_after := is_instance_valid(_faller)
    var line := "area_%s entry1_frame=%d cb_cls=%s cb_monitoring=%s" % [
        kind, entry1, in_cb.get("cls", "-"), in_cb.get("monitoring", "-")]
    line += " cb_readback=%s cb_queued=%s cb_freed=%s" % [
        in_cb.get("readback", "-"), in_cb.get("queued", "-"), in_cb.get("freed", "-")]
    line += " cb_srv_before=%s cb_srv_read=%s cb_node_read=%s" % [
        in_cb.get("srv_before", "-"), in_cb.get("srv_read", "-"), in_cb.get("node_read", "-")]
    line += " next_node=%s next_srv=%s late_node=%s node_write_stuck=%s node_follows_srv=%s valid_after=%s post_monitoring=%s entries=%d exits=%d" % [
        next_node, next_srv, late_node, stuck, follows, valid_after,
        _area.monitoring, _area_entries, _area_exits]
    if kind == "dss_in_cb":
        line += " cb_dss_null=%s cb_q_hits=%s" % [
            in_cb.get("dss_null", "-"), in_cb.get("q_hits", "-")]
    _finish(line)
