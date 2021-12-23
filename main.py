
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import TextNode
from panda3d.core import LVector3
from direct.gui.OnscreenText import OnscreenText
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func, Wait
from direct.actor import Actor
from random import random
import sys


class BoxingRobotDemo(ShowBase):
    # Fungsi seperti makro yang digunakan untuk mengurangi jumlah kode yang diperlukan untuk membuat
    # petunjuk di layar

    def genLabelText(self, text, i):
        return OnscreenText(text=text, parent=base.a2dTopLeft, scale=.05,
                            pos=(0.1, - 0.1 -.07 * i), fg=(1, 1, 1, 1),
                            align=TextNode.ALeft)

    def __init__(self):
        # Inisialisasi kelas ShowBase dari mana kita mewarisi, yang akan
        # buat jendela dan atur semua yang kita butuhkan untuk rendering ke dalamnya.
        ShowBase.__init__(self)

        # Kode ini menempatkan judul standar dan teks instruksi di layar
        self.title = OnscreenText(text="Panda3D: Tutorial - Actors",
                                  parent=base.a2dBottomRight, style=1,
                                  fg=(0, 0, 0, 1), pos=(-0.2, 0.1),
                                  align=TextNode.ARight, scale=.09)

        self.escapeEventText = self.genLabelText("ESC: Quit", 0)
        self.akeyEventText = self.genLabelText("[A]: Robot 1 Left Punch", 1)
        self.skeyEventText = self.genLabelText("[S]: Robot 1 Right Punch", 2)
        self.kkeyEventText = self.genLabelText("[K]: Robot 2 Left Punch", 3)
        self.lkeyEventText = self.genLabelText("[L]: Robot 2 Right Punch", 4)

        # Atur kamera pada posisi tetap
        self.disableMouse()
        camera.setPosHpr(14.5, -15.4, 14, 45, -14, 0)
        self.setBackgroundColor(0, 0, 0)

        # Tambahkan pencahayaan agar objek tidak tergambar rata
        self.setupLights()

        # Load the ring
        self.ring = loader.loadModel('models/ring')
        self.ring.reparentTo(render)

         
        self.robot1 = Actor.Actor('models/robot',
                                  {'leftPunch': 'models/robot_left_punch',
                                   'rightPunch': 'models/robot_right_punch',
                                   'headUp': 'models/robot_head_up',
                                   'headDown': 'models/robot_head_down'})

        # Aktor perlu diposisikan dan diasuh seperti objek normal
        self.robot1.setPosHprScale(-1, -2.5, 4, 45, 0, 0, 1.25, 1.25, 1.25)
        self.robot1.reparentTo(render)

        # akan mengulangi proses untuk robot kedua. Satu-satunya hal yang berubah
         #ini dia warna dan posisi robotnya
        self.robot2 = Actor.Actor('models/robot',
                                  {'leftPunch': 'models/robot_left_punch',
                                   'rightPunch': 'models/robot_right_punch',
                                   'headUp': 'models/robot_head_up',
                                   'headDown': 'models/robot_head_down'})

        # untuk mengatur properti robot
        self.robot2.setPosHprScale(1, 1.5, 4, 225, 0, 0, 1.25, 1.25, 1.25)
        self.robot2.setColor((.7, 0, 0, 1))
        self.robot2.reparentTo(render)


        # Urutan pukulan untuk lengan kiri robot 1
        self.robot1.punchLeft = Sequence(
            # Interval untuk animasi terentang
            self.robot1.actorInterval('leftPunch', startFrame=1, endFrame=10),
            # Berfungsi untuk memeriksa apakah pukulan berhasil
            Func(self.checkPunch, 2),
            # Interval untuk animasi retraksi
            self.robot1.actorInterval('leftPunch', startFrame=11, endFrame=32))

       # Urutan pukulan untuk lengan kanan robot 1
        self.robot1.punchRight = Sequence(
            self.robot1.actorInterval('rightPunch', startFrame=1, endFrame=10),
            Func(self.checkPunch, 2),
            self.robot1.actorInterval('rightPunch', startFrame=11, endFrame=32))

       # Urutan pukulan untuk lengan kiri robot 2
        self.robot2.punchLeft = Sequence(
            self.robot2.actorInterval('leftPunch', startFrame=1, endFrame=10),
            Func(self.checkPunch, 1),
            self.robot2.actorInterval('leftPunch', startFrame=11, endFrame=32))

        # Urutan pukulan untuk lengan kanan robot 2
        self.robot2.punchRight = Sequence(
            self.robot2.actorInterval('rightPunch', startFrame=1, endFrame=10),
            Func(self.checkPunch, 1),
            self.robot2.actorInterval('rightPunch', startFrame=11, endFrame=32))

        # menggunakan teknik yang sama untuk membuat urutan saat robot terlempar 
        # keluar di mana kepala muncul, menunggu beberapa saat, dan kemudian me-reset

       # Animasi kepala untuk robot 1
        self.robot1.resetHead = Sequence(
            # Interval untuk kepala naik. Karena tidak ada bingkai awal atau akhir yang diberikan,
            # seluruh animasi diputar.
            self.robot1.actorInterval('headUp'),
            Wait(1.5),
            # Animasi kepala ke bawah dianimasikan sedikit terlalu cepat, jadi ini akan
             # mainkan dengan kecepatan 75% dari kecepatan normalnya
            self.robot1.actorInterval('headDown', playRate=.75))

        # Animasi kepala untuk robot 2
        self.robot2.resetHead = Sequence(
            self.robot2.actorInterval('headUp'),
            Wait(1.5),
            self.robot2.actorInterval('headDown', playRate=.75))

         # Setelah mendefinisikan gerakan, kita dapat menentukan input kunci kita.
         # Setiap kepalan tangan terikat pada sebuah kunci. Saat tombol ditekan, self.tryPunch memeriksa untuk
         # pastikan kedua robot menundukkan kepala, dan jika mereka melakukannya
         # memainkan interval yang diberikan
        self.accept('escape', sys.exit)
        self.accept('a', self.tryPunch, [self.robot1.punchLeft])
        self.accept('s', self.tryPunch, [self.robot1.punchRight])
        self.accept('k', self.tryPunch, [self.robot2.punchLeft])
        self.accept('l', self.tryPunch, [self.robot2.punchRight])

     # tryPunch akan memainkan interval yang diberikan hanya jika
     # tidak ada robot yang memainkan 'resetHead' (kepala terangkat)
     # interval pukulan yang diberikan belum diputar
    def tryPunch(self, interval):
        if (not self.robot1.resetHead.isPlaying() and
                not self.robot2.resetHead.isPlaying() and
                not interval.isPlaying()):
            interval.start()

    # checkPunch akan menentukan apakah pukulan berhasil dilempar
    def checkPunch(self, robot):
        if robot == 1:
            
            if self.robot1.resetHead.isPlaying():
                return
            
            if (not self.robot1.punchLeft.isPlaying() and
                    not self.robot1.punchRight.isPlaying()):
            
                if random() > .85:
                    self.robot1.resetHead.start()
            elif random() > .95:
                self.robot1.resetHead.start()
        else:
            # pukulan diarahkan ke robot 2, sama seperti di atas
            if self.robot2.resetHead.isPlaying():
                return
            if (not self.robot2.punchLeft.isPlaying() and
                    not self.robot2.punchRight.isPlaying()):
                if random() > .85:
                    self.robot2.resetHead.start()
            elif random() > .95:
                self.robot2.resetHead.start()

    # Fungsi ini mengatur pencahayaan
    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .75, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 0, -2.5))
        directionalLight.setColor((0.9, 0.8, 0.9, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

demo = BoxingRobotDemo()
demo.run()
