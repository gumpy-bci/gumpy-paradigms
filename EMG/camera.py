# -*- coding: utf-8 -*-
from direct.showbase import DirectObject 
from pandac.PandaModules import Vec3, WindowProperties
from direct.gui.OnscreenText import OnscreenText
import math

class CamFree(DirectObject.DirectObject):
    def __init__(self):
        base.disableMouse()

        self.keyMap = {"FORWARD":0, "BACK":0, "RIGHT":0, "LEFT":0, "Mouse3":0, "LSHIFT":0, "UPWARDS":0, "DOWNWARDS":0}
        self.accept("w", self.setKey, ["FORWARD",1])
        self.accept("w-up", self.setKey, ["FORWARD",0])
        self.accept("s", self.setKey, ["BACK",1])
        self.accept("s-up", self.setKey, ["BACK",0])
        self.accept("d", self.setKey, ["RIGHT",1])
        self.accept("d-up", self.setKey, ["RIGHT",0])
        self.accept("a", self.setKey, ["LEFT",1])
        self.accept("a-up", self.setKey, ["LEFT",0])
        self.accept("q", self.setKey, ["UPWARDS",1])
        self.accept("q-up", self.setKey, ["UPWARDS",0])
        self.accept("e", self.setKey, ["DOWNWARDS",1])
        self.accept("e-up", self.setKey, ["DOWNWARDS",0])
        self.accept("mouse3", self.setKey, ["Mouse3",1])
        self.accept("mouse3-up", self.setKey, ["Mouse3",0])
        self.accept("lshift", self.setKey, ["LSHIFT",1])
        self.accept("lshift-up", self.setKey, ["LSHIFT",0])
        self.accept("wheel_up", self.CamSpeed, [1.1])
        self.accept("wheel_down", self.CamSpeed, [0.9])
        
        self.SpeedCam = 0.1 # Скорость перемещения камеры
        self.SpeedRot = 0.05 # Скорость врашения камеры
        self.SpeedMult = 5 # Множитель скорости камеры при нажатии lshift
        
        self.textSpeed = OnscreenText(pos = (0.9, -0.9), scale = 0.1)
        
        self.CursorOffOn = 'On'
        
        self.props = WindowProperties()
        
        taskMgr.add(self.CamControl, 'CamControl') #менеджер для запуска функции
        
    def setKey(self, key, value): # Функция для перезаписи в словарь "keyMap" ключа и значения
        self.keyMap[key] = value
        
    def CamSpeed(self, sd): # Функция изменения скорости камеры
        self.SpeedCam *= sd
        
    def CamControl(self, task): # Функция управления камерой
        if (self.keyMap["Mouse3"] != 0): # Управление камерой если зажата правая кнопка мыши
            self.textSpeed.show()
            if (self.CursorOffOn == 'On'):
                self.props.setCursorHidden(True)
                base.win.requestProperties(self.props)
                self.CursorOffOn = 'Off'
            
            dirFB = base.camera.getMat().getRow3(1)
            dirRL = base.camera.getMat().getRow3(0)

            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            
            Speed = self.SpeedCam
            
            if (self.keyMap["LSHIFT"]!=0):
                Speed = self.SpeedCam*self.SpeedMult
            if (self.keyMap["FORWARD"]!=0):
                camera.setPos(camera.getPos()+dirFB*Speed)
            if (self.keyMap["BACK"]!=0):
                camera.setPos(camera.getPos()-dirFB*Speed)
            if (self.keyMap["RIGHT"]!=0):
                camera.setPos(camera.getPos()+dirRL*Speed)
            if (self.keyMap["LEFT"]!=0):
                camera.setPos(camera.getPos()-dirRL*Speed)
            if (self.keyMap["UPWARDS"]!=0):
                camera.setZ(camera.getZ()+Speed)
            if (self.keyMap["DOWNWARDS"]!=0):
                camera.setZ(camera.getZ()-Speed)
                
            if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                camera.setH(camera.getH() -  (x - base.win.getXSize()/2)*self.SpeedRot) 
                camera.setP(camera.getP() - (y - base.win.getYSize()/2)*self.SpeedRot)
                if (camera.getP()<=-90.1):
                    camera.setP(-90)
                if (camera.getP()>=90.1):
                    camera.setP(90)
                    
            self.textSpeed.setText('Speed: '+str("%.4f" % Speed)) # устанавливаем и округляем значение скорости(!округляем только выводимую на экран)
        else:
            self.textSpeed.hide()
            self.CursorOffOn = 'On'
            self.props.setCursorHidden(False)
            base.win.requestProperties(self.props)
                
        return task.cont