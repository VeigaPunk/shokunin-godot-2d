extends SceneTree
# r88-critic minimal startup-mode probe: same arm shape as r88_surfaces.gd's
# sprite_phys (deferred _run, body at (250,-50), 30 awaited physics frames),
# but with a minimal file so engine+script startup cost is lower.
func _initialize() -> void:
	print("T0 %d" % Time.get_ticks_usec())
	call_deferred("_run")

func _run() -> void:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(250, -50)
	b.gravity_scale = 1.0
	root.add_child(b)
	var first_v := ""
	for i in 30:
		await physics_frame
		if i == 0:
			first_v = str(b.linear_velocity)
	print("PASS r88_min mode first_v=%s y30=%.4f phys_frames=%d" % [
		first_v, b.global_position.y, Engine.get_physics_frames()])
	quit(0)

# inflation control: unused compiled functions (code volume, not behavior)
func _pad0() -> int:
	return 0
func _pad1() -> int:
	return 1
func _pad2() -> int:
	return 2
func _pad3() -> int:
	return 3
func _pad4() -> int:
	return 4
func _pad5() -> int:
	return 5
func _pad6() -> int:
	return 6
func _pad7() -> int:
	return 7
func _pad8() -> int:
	return 8
func _pad9() -> int:
	return 9
func _pad10() -> int:
	return 10
func _pad11() -> int:
	return 11
func _pad12() -> int:
	return 12
func _pad13() -> int:
	return 13
func _pad14() -> int:
	return 14
func _pad15() -> int:
	return 15
func _pad16() -> int:
	return 16
func _pad17() -> int:
	return 17
func _pad18() -> int:
	return 18
func _pad19() -> int:
	return 19
func _pad20() -> int:
	return 20
func _pad21() -> int:
	return 21
func _pad22() -> int:
	return 22
func _pad23() -> int:
	return 23
func _pad24() -> int:
	return 24
func _pad25() -> int:
	return 25
func _pad26() -> int:
	return 26
func _pad27() -> int:
	return 27
func _pad28() -> int:
	return 28
func _pad29() -> int:
	return 29
func _pad30() -> int:
	return 30
func _pad31() -> int:
	return 31
func _pad32() -> int:
	return 32
func _pad33() -> int:
	return 33
func _pad34() -> int:
	return 34
func _pad35() -> int:
	return 35
func _pad36() -> int:
	return 36
func _pad37() -> int:
	return 37
func _pad38() -> int:
	return 38
func _pad39() -> int:
	return 39
func _pad40() -> int:
	return 40
func _pad41() -> int:
	return 41
func _pad42() -> int:
	return 42
func _pad43() -> int:
	return 43
func _pad44() -> int:
	return 44
func _pad45() -> int:
	return 45
func _pad46() -> int:
	return 46
func _pad47() -> int:
	return 47
func _pad48() -> int:
	return 48
func _pad49() -> int:
	return 49
func _pad50() -> int:
	return 50
func _pad51() -> int:
	return 51
func _pad52() -> int:
	return 52
func _pad53() -> int:
	return 53
func _pad54() -> int:
	return 54
func _pad55() -> int:
	return 55
func _pad56() -> int:
	return 56
func _pad57() -> int:
	return 57
func _pad58() -> int:
	return 58
func _pad59() -> int:
	return 59
func _pad60() -> int:
	return 60
func _pad61() -> int:
	return 61
func _pad62() -> int:
	return 62
func _pad63() -> int:
	return 63
func _pad64() -> int:
	return 64
func _pad65() -> int:
	return 65
func _pad66() -> int:
	return 66
func _pad67() -> int:
	return 67
func _pad68() -> int:
	return 68
func _pad69() -> int:
	return 69
func _pad70() -> int:
	return 70
func _pad71() -> int:
	return 71
func _pad72() -> int:
	return 72
func _pad73() -> int:
	return 73
func _pad74() -> int:
	return 74
func _pad75() -> int:
	return 75
func _pad76() -> int:
	return 76
func _pad77() -> int:
	return 77
func _pad78() -> int:
	return 78
func _pad79() -> int:
	return 79
func _pad80() -> int:
	return 80
func _pad81() -> int:
	return 81
func _pad82() -> int:
	return 82
func _pad83() -> int:
	return 83
func _pad84() -> int:
	return 84
func _pad85() -> int:
	return 85
func _pad86() -> int:
	return 86
func _pad87() -> int:
	return 87
func _pad88() -> int:
	return 88
func _pad89() -> int:
	return 89
func _pad90() -> int:
	return 90
func _pad91() -> int:
	return 91
func _pad92() -> int:
	return 92
func _pad93() -> int:
	return 93
func _pad94() -> int:
	return 94
func _pad95() -> int:
	return 95
func _pad96() -> int:
	return 96
func _pad97() -> int:
	return 97
func _pad98() -> int:
	return 98
func _pad99() -> int:
	return 99
func _pad100() -> int:
	return 100
func _pad101() -> int:
	return 101
func _pad102() -> int:
	return 102
func _pad103() -> int:
	return 103
func _pad104() -> int:
	return 104
func _pad105() -> int:
	return 105
func _pad106() -> int:
	return 106
func _pad107() -> int:
	return 107
func _pad108() -> int:
	return 108
func _pad109() -> int:
	return 109
func _pad110() -> int:
	return 110
func _pad111() -> int:
	return 111
func _pad112() -> int:
	return 112
func _pad113() -> int:
	return 113
func _pad114() -> int:
	return 114
func _pad115() -> int:
	return 115
func _pad116() -> int:
	return 116
func _pad117() -> int:
	return 117
func _pad118() -> int:
	return 118
func _pad119() -> int:
	return 119
func _pad120() -> int:
	return 120
func _pad121() -> int:
	return 121
func _pad122() -> int:
	return 122
func _pad123() -> int:
	return 123
func _pad124() -> int:
	return 124
func _pad125() -> int:
	return 125
func _pad126() -> int:
	return 126
func _pad127() -> int:
	return 127
func _pad128() -> int:
	return 128
func _pad129() -> int:
	return 129
func _pad130() -> int:
	return 130
func _pad131() -> int:
	return 131
func _pad132() -> int:
	return 132
func _pad133() -> int:
	return 133
func _pad134() -> int:
	return 134
func _pad135() -> int:
	return 135
func _pad136() -> int:
	return 136
func _pad137() -> int:
	return 137
func _pad138() -> int:
	return 138
func _pad139() -> int:
	return 139
func _pad140() -> int:
	return 140
func _pad141() -> int:
	return 141
func _pad142() -> int:
	return 142
func _pad143() -> int:
	return 143
func _pad144() -> int:
	return 144
func _pad145() -> int:
	return 145
func _pad146() -> int:
	return 146
func _pad147() -> int:
	return 147
func _pad148() -> int:
	return 148
func _pad149() -> int:
	return 149
func _pad150() -> int:
	return 150
func _pad151() -> int:
	return 151
func _pad152() -> int:
	return 152
func _pad153() -> int:
	return 153
func _pad154() -> int:
	return 154
func _pad155() -> int:
	return 155
func _pad156() -> int:
	return 156
func _pad157() -> int:
	return 157
func _pad158() -> int:
	return 158
func _pad159() -> int:
	return 159
func _pad160() -> int:
	return 160
func _pad161() -> int:
	return 161
func _pad162() -> int:
	return 162
func _pad163() -> int:
	return 163
func _pad164() -> int:
	return 164
func _pad165() -> int:
	return 165
func _pad166() -> int:
	return 166
func _pad167() -> int:
	return 167
func _pad168() -> int:
	return 168
func _pad169() -> int:
	return 169
func _pad170() -> int:
	return 170
func _pad171() -> int:
	return 171
func _pad172() -> int:
	return 172
func _pad173() -> int:
	return 173
func _pad174() -> int:
	return 174
func _pad175() -> int:
	return 175
func _pad176() -> int:
	return 176
func _pad177() -> int:
	return 177
func _pad178() -> int:
	return 178
func _pad179() -> int:
	return 179
func _pad180() -> int:
	return 180
func _pad181() -> int:
	return 181
func _pad182() -> int:
	return 182
func _pad183() -> int:
	return 183
func _pad184() -> int:
	return 184
func _pad185() -> int:
	return 185
func _pad186() -> int:
	return 186
func _pad187() -> int:
	return 187
func _pad188() -> int:
	return 188
func _pad189() -> int:
	return 189
func _pad190() -> int:
	return 190
func _pad191() -> int:
	return 191
func _pad192() -> int:
	return 192
func _pad193() -> int:
	return 193
func _pad194() -> int:
	return 194
func _pad195() -> int:
	return 195
func _pad196() -> int:
	return 196
func _pad197() -> int:
	return 197
func _pad198() -> int:
	return 198
func _pad199() -> int:
	return 199
func _pad200() -> int:
	return 200
func _pad201() -> int:
	return 201
func _pad202() -> int:
	return 202
func _pad203() -> int:
	return 203
func _pad204() -> int:
	return 204
func _pad205() -> int:
	return 205
func _pad206() -> int:
	return 206
func _pad207() -> int:
	return 207
func _pad208() -> int:
	return 208
func _pad209() -> int:
	return 209
func _pad210() -> int:
	return 210
func _pad211() -> int:
	return 211
func _pad212() -> int:
	return 212
func _pad213() -> int:
	return 213
func _pad214() -> int:
	return 214
func _pad215() -> int:
	return 215
func _pad216() -> int:
	return 216
func _pad217() -> int:
	return 217
func _pad218() -> int:
	return 218
func _pad219() -> int:
	return 219
func _pad220() -> int:
	return 220
func _pad221() -> int:
	return 221
func _pad222() -> int:
	return 222
func _pad223() -> int:
	return 223
func _pad224() -> int:
	return 224
func _pad225() -> int:
	return 225
func _pad226() -> int:
	return 226
func _pad227() -> int:
	return 227
func _pad228() -> int:
	return 228
func _pad229() -> int:
	return 229
func _pad230() -> int:
	return 230
func _pad231() -> int:
	return 231
func _pad232() -> int:
	return 232
func _pad233() -> int:
	return 233
func _pad234() -> int:
	return 234
func _pad235() -> int:
	return 235
func _pad236() -> int:
	return 236
func _pad237() -> int:
	return 237
func _pad238() -> int:
	return 238
func _pad239() -> int:
	return 239
func _pad240() -> int:
	return 240
func _pad241() -> int:
	return 241
func _pad242() -> int:
	return 242
func _pad243() -> int:
	return 243
func _pad244() -> int:
	return 244
func _pad245() -> int:
	return 245
func _pad246() -> int:
	return 246
func _pad247() -> int:
	return 247
func _pad248() -> int:
	return 248
func _pad249() -> int:
	return 249
func _pad250() -> int:
	return 250
func _pad251() -> int:
	return 251
func _pad252() -> int:
	return 252
func _pad253() -> int:
	return 253
func _pad254() -> int:
	return 254
func _pad255() -> int:
	return 255
func _pad256() -> int:
	return 256
func _pad257() -> int:
	return 257
func _pad258() -> int:
	return 258
func _pad259() -> int:
	return 259
func _pad260() -> int:
	return 260
func _pad261() -> int:
	return 261
func _pad262() -> int:
	return 262
func _pad263() -> int:
	return 263
func _pad264() -> int:
	return 264
func _pad265() -> int:
	return 265
func _pad266() -> int:
	return 266
func _pad267() -> int:
	return 267
func _pad268() -> int:
	return 268
func _pad269() -> int:
	return 269
func _pad270() -> int:
	return 270
func _pad271() -> int:
	return 271
func _pad272() -> int:
	return 272
func _pad273() -> int:
	return 273
func _pad274() -> int:
	return 274
func _pad275() -> int:
	return 275
func _pad276() -> int:
	return 276
func _pad277() -> int:
	return 277
func _pad278() -> int:
	return 278
func _pad279() -> int:
	return 279
func _pad280() -> int:
	return 280
func _pad281() -> int:
	return 281
func _pad282() -> int:
	return 282
func _pad283() -> int:
	return 283
func _pad284() -> int:
	return 284
func _pad285() -> int:
	return 285
func _pad286() -> int:
	return 286
func _pad287() -> int:
	return 287
func _pad288() -> int:
	return 288
func _pad289() -> int:
	return 289
func _pad290() -> int:
	return 290
func _pad291() -> int:
	return 291
func _pad292() -> int:
	return 292
func _pad293() -> int:
	return 293
func _pad294() -> int:
	return 294
func _pad295() -> int:
	return 295
func _pad296() -> int:
	return 296
func _pad297() -> int:
	return 297
func _pad298() -> int:
	return 298
func _pad299() -> int:
	return 299
func _pad300() -> int:
	return 300
func _pad301() -> int:
	return 301
func _pad302() -> int:
	return 302
func _pad303() -> int:
	return 303
func _pad304() -> int:
	return 304
func _pad305() -> int:
	return 305
func _pad306() -> int:
	return 306
func _pad307() -> int:
	return 307
func _pad308() -> int:
	return 308
func _pad309() -> int:
	return 309
func _pad310() -> int:
	return 310
func _pad311() -> int:
	return 311
func _pad312() -> int:
	return 312
func _pad313() -> int:
	return 313
func _pad314() -> int:
	return 314
func _pad315() -> int:
	return 315
func _pad316() -> int:
	return 316
func _pad317() -> int:
	return 317
func _pad318() -> int:
	return 318
func _pad319() -> int:
	return 319
func _pad320() -> int:
	return 320
func _pad321() -> int:
	return 321
func _pad322() -> int:
	return 322
func _pad323() -> int:
	return 323
func _pad324() -> int:
	return 324
func _pad325() -> int:
	return 325
func _pad326() -> int:
	return 326
func _pad327() -> int:
	return 327
func _pad328() -> int:
	return 328
func _pad329() -> int:
	return 329
func _pad330() -> int:
	return 330
func _pad331() -> int:
	return 331
func _pad332() -> int:
	return 332
func _pad333() -> int:
	return 333
func _pad334() -> int:
	return 334
func _pad335() -> int:
	return 335
func _pad336() -> int:
	return 336
func _pad337() -> int:
	return 337
func _pad338() -> int:
	return 338
func _pad339() -> int:
	return 339
func _pad340() -> int:
	return 340
func _pad341() -> int:
	return 341
func _pad342() -> int:
	return 342
func _pad343() -> int:
	return 343
func _pad344() -> int:
	return 344
func _pad345() -> int:
	return 345
func _pad346() -> int:
	return 346
func _pad347() -> int:
	return 347
func _pad348() -> int:
	return 348
func _pad349() -> int:
	return 349
func _pad350() -> int:
	return 350
func _pad351() -> int:
	return 351
func _pad352() -> int:
	return 352
func _pad353() -> int:
	return 353
func _pad354() -> int:
	return 354
func _pad355() -> int:
	return 355
func _pad356() -> int:
	return 356
func _pad357() -> int:
	return 357
func _pad358() -> int:
	return 358
func _pad359() -> int:
	return 359
func _pad360() -> int:
	return 360
func _pad361() -> int:
	return 361
func _pad362() -> int:
	return 362
func _pad363() -> int:
	return 363
func _pad364() -> int:
	return 364
func _pad365() -> int:
	return 365
func _pad366() -> int:
	return 366
func _pad367() -> int:
	return 367
func _pad368() -> int:
	return 368
func _pad369() -> int:
	return 369
func _pad370() -> int:
	return 370
func _pad371() -> int:
	return 371
func _pad372() -> int:
	return 372
func _pad373() -> int:
	return 373
func _pad374() -> int:
	return 374
func _pad375() -> int:
	return 375
func _pad376() -> int:
	return 376
func _pad377() -> int:
	return 377
func _pad378() -> int:
	return 378
func _pad379() -> int:
	return 379
func _pad380() -> int:
	return 380
func _pad381() -> int:
	return 381
func _pad382() -> int:
	return 382
func _pad383() -> int:
	return 383
func _pad384() -> int:
	return 384
func _pad385() -> int:
	return 385
func _pad386() -> int:
	return 386
func _pad387() -> int:
	return 387
func _pad388() -> int:
	return 388
func _pad389() -> int:
	return 389
func _pad390() -> int:
	return 390
func _pad391() -> int:
	return 391
func _pad392() -> int:
	return 392
func _pad393() -> int:
	return 393
func _pad394() -> int:
	return 394
func _pad395() -> int:
	return 395
func _pad396() -> int:
	return 396
func _pad397() -> int:
	return 397
func _pad398() -> int:
	return 398
func _pad399() -> int:
	return 399
func _pad400() -> int:
	return 400
func _pad401() -> int:
	return 401
func _pad402() -> int:
	return 402
func _pad403() -> int:
	return 403
func _pad404() -> int:
	return 404
func _pad405() -> int:
	return 405
func _pad406() -> int:
	return 406
func _pad407() -> int:
	return 407
func _pad408() -> int:
	return 408
func _pad409() -> int:
	return 409
func _pad410() -> int:
	return 410
func _pad411() -> int:
	return 411
func _pad412() -> int:
	return 412
func _pad413() -> int:
	return 413
func _pad414() -> int:
	return 414
func _pad415() -> int:
	return 415
func _pad416() -> int:
	return 416
func _pad417() -> int:
	return 417
func _pad418() -> int:
	return 418
func _pad419() -> int:
	return 419
func _pad420() -> int:
	return 420
func _pad421() -> int:
	return 421
func _pad422() -> int:
	return 422
func _pad423() -> int:
	return 423
func _pad424() -> int:
	return 424
func _pad425() -> int:
	return 425
func _pad426() -> int:
	return 426
func _pad427() -> int:
	return 427
func _pad428() -> int:
	return 428
func _pad429() -> int:
	return 429
func _pad430() -> int:
	return 430
func _pad431() -> int:
	return 431
func _pad432() -> int:
	return 432
func _pad433() -> int:
	return 433
func _pad434() -> int:
	return 434
func _pad435() -> int:
	return 435
func _pad436() -> int:
	return 436
func _pad437() -> int:
	return 437
func _pad438() -> int:
	return 438
func _pad439() -> int:
	return 439
func _pad440() -> int:
	return 440
func _pad441() -> int:
	return 441
func _pad442() -> int:
	return 442
func _pad443() -> int:
	return 443
func _pad444() -> int:
	return 444
func _pad445() -> int:
	return 445
func _pad446() -> int:
	return 446
func _pad447() -> int:
	return 447
func _pad448() -> int:
	return 448
func _pad449() -> int:
	return 449
func _pad450() -> int:
	return 450
func _pad451() -> int:
	return 451
func _pad452() -> int:
	return 452
func _pad453() -> int:
	return 453
func _pad454() -> int:
	return 454
func _pad455() -> int:
	return 455
func _pad456() -> int:
	return 456
func _pad457() -> int:
	return 457
func _pad458() -> int:
	return 458
func _pad459() -> int:
	return 459
func _pad460() -> int:
	return 460
func _pad461() -> int:
	return 461
func _pad462() -> int:
	return 462
func _pad463() -> int:
	return 463
func _pad464() -> int:
	return 464
func _pad465() -> int:
	return 465
func _pad466() -> int:
	return 466
func _pad467() -> int:
	return 467
func _pad468() -> int:
	return 468
func _pad469() -> int:
	return 469
func _pad470() -> int:
	return 470
func _pad471() -> int:
	return 471
func _pad472() -> int:
	return 472
func _pad473() -> int:
	return 473
func _pad474() -> int:
	return 474
func _pad475() -> int:
	return 475
func _pad476() -> int:
	return 476
func _pad477() -> int:
	return 477
func _pad478() -> int:
	return 478
func _pad479() -> int:
	return 479
func _pad480() -> int:
	return 480
func _pad481() -> int:
	return 481
func _pad482() -> int:
	return 482
func _pad483() -> int:
	return 483
func _pad484() -> int:
	return 484
func _pad485() -> int:
	return 485
func _pad486() -> int:
	return 486
func _pad487() -> int:
	return 487
func _pad488() -> int:
	return 488
func _pad489() -> int:
	return 489
func _pad490() -> int:
	return 490
func _pad491() -> int:
	return 491
func _pad492() -> int:
	return 492
func _pad493() -> int:
	return 493
func _pad494() -> int:
	return 494
func _pad495() -> int:
	return 495
func _pad496() -> int:
	return 496
func _pad497() -> int:
	return 497
func _pad498() -> int:
	return 498
func _pad499() -> int:
	return 499
func _pad500() -> int:
	return 500
func _pad501() -> int:
	return 501
func _pad502() -> int:
	return 502
func _pad503() -> int:
	return 503
func _pad504() -> int:
	return 504
func _pad505() -> int:
	return 505
func _pad506() -> int:
	return 506
func _pad507() -> int:
	return 507
func _pad508() -> int:
	return 508
func _pad509() -> int:
	return 509
func _pad510() -> int:
	return 510
func _pad511() -> int:
	return 511
func _pad512() -> int:
	return 512
func _pad513() -> int:
	return 513
func _pad514() -> int:
	return 514
func _pad515() -> int:
	return 515
func _pad516() -> int:
	return 516
func _pad517() -> int:
	return 517
func _pad518() -> int:
	return 518
func _pad519() -> int:
	return 519
func _pad520() -> int:
	return 520
func _pad521() -> int:
	return 521
func _pad522() -> int:
	return 522
func _pad523() -> int:
	return 523
func _pad524() -> int:
	return 524
func _pad525() -> int:
	return 525
func _pad526() -> int:
	return 526
func _pad527() -> int:
	return 527
func _pad528() -> int:
	return 528
func _pad529() -> int:
	return 529
func _pad530() -> int:
	return 530
func _pad531() -> int:
	return 531
func _pad532() -> int:
	return 532
func _pad533() -> int:
	return 533
func _pad534() -> int:
	return 534
func _pad535() -> int:
	return 535
func _pad536() -> int:
	return 536
func _pad537() -> int:
	return 537
func _pad538() -> int:
	return 538
func _pad539() -> int:
	return 539
func _pad540() -> int:
	return 540
func _pad541() -> int:
	return 541
func _pad542() -> int:
	return 542
func _pad543() -> int:
	return 543
func _pad544() -> int:
	return 544
func _pad545() -> int:
	return 545
func _pad546() -> int:
	return 546
func _pad547() -> int:
	return 547
func _pad548() -> int:
	return 548
func _pad549() -> int:
	return 549
func _pad550() -> int:
	return 550
func _pad551() -> int:
	return 551
func _pad552() -> int:
	return 552
func _pad553() -> int:
	return 553
func _pad554() -> int:
	return 554
func _pad555() -> int:
	return 555
func _pad556() -> int:
	return 556
func _pad557() -> int:
	return 557
func _pad558() -> int:
	return 558
func _pad559() -> int:
	return 559
func _pad560() -> int:
	return 560
func _pad561() -> int:
	return 561
func _pad562() -> int:
	return 562
func _pad563() -> int:
	return 563
func _pad564() -> int:
	return 564
func _pad565() -> int:
	return 565
func _pad566() -> int:
	return 566
func _pad567() -> int:
	return 567
func _pad568() -> int:
	return 568
func _pad569() -> int:
	return 569
func _pad570() -> int:
	return 570
func _pad571() -> int:
	return 571
func _pad572() -> int:
	return 572
func _pad573() -> int:
	return 573
func _pad574() -> int:
	return 574
func _pad575() -> int:
	return 575
func _pad576() -> int:
	return 576
func _pad577() -> int:
	return 577
func _pad578() -> int:
	return 578
func _pad579() -> int:
	return 579
func _pad580() -> int:
	return 580
func _pad581() -> int:
	return 581
func _pad582() -> int:
	return 582
func _pad583() -> int:
	return 583
func _pad584() -> int:
	return 584
func _pad585() -> int:
	return 585
func _pad586() -> int:
	return 586
func _pad587() -> int:
	return 587
func _pad588() -> int:
	return 588
func _pad589() -> int:
	return 589
func _pad590() -> int:
	return 590
func _pad591() -> int:
	return 591
func _pad592() -> int:
	return 592
func _pad593() -> int:
	return 593
func _pad594() -> int:
	return 594
func _pad595() -> int:
	return 595
func _pad596() -> int:
	return 596
func _pad597() -> int:
	return 597
func _pad598() -> int:
	return 598
func _pad599() -> int:
	return 599
