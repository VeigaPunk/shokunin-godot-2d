extends SceneTree

func _initialize() -> void:
    var no_play := "--no-play" in OS.get_cmdline_user_args()
    var stream := AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.mix_rate = 22050
    stream.stereo = false
    var samples := PackedByteArray()
    for index in range(22050):
        var sample := int(sin(TAU * 440.0 * float(index) / 22050.0) * 8191.0)
        samples.append(sample & 0xff)
        samples.append((sample >> 8) & 0xff)
    stream.data = samples

    var player := AudioStreamPlayer.new()
    player.name = "FixtureAudioPlayer"
    player.stream = stream
    root.add_child(player)
    await process_frame
    var in_tree := player.is_inside_tree()
    if not no_play:
        player.play()
    var position_before := player.get_playback_position()

    # Bound observation to 12 rendered process frames; do not wait on audio duration.
    for frame in range(12):
        await process_frame
    var playing := player.is_playing()
    var position_after := player.get_playback_position()
    var advanced := position_after > position_before + 0.001
    var assertion := in_tree and playing and advanced
    var generated_bytes := samples.size()
    player.stop()
    player.stream = null
    player.free()
    stream = null
    samples.clear()
    for frame in range(120):
        await process_frame
    if not assertion:
        push_error("AUDIO ASSERTION FAILED: expected in-tree player playback to advance, in_tree=%s playing=%s position_before=%s position_after=%s" % [in_tree, playing, position_before, position_after])
        quit(2)
        return
    print("PASS audio_playback in_tree=true playing=true position_advanced=true position_before=%s position_after=%s generated_samples=%s" % [position_before, position_after, generated_bytes])
    quit(0)
