extends SceneTree
func _initialize():
 print("RadioButton exists=", ClassDB.class_exists("RadioButton"))
 print("CheckBox exists=", ClassDB.class_exists("CheckBox"))
 quit()
