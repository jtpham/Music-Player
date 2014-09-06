import sys
import sip
sip.setapi('QString',2) # necessary if running on Python 2.7 and below
from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon
from random import shuffle

class MediaPlayer(QtGui.QMainWindow):
    #Initialize the GUI and engine. 
    #Set objects in this class and connect it to the engine
    def __init__(self):
        super(MediaPlayer, self).__init__()

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)
        self.mediaObject.setTickInterval(1000)
        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.metaInformationResolver.stateChanged.connect(self.metaStateChanged)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)
        self.mediaObject.aboutToFinish.connect(self.aboutToFinish)
        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.setupActions()
        self.setupMenuBar()
        self.setupUi()
        self.sources = []

    #setupActions creates all the buttons and calls a respective function with every button press
    #For example, playAction will create a Play button and a keyboard shortcut
    #Pressing the button will trigger the function self.mediaObject.play
    def setupActions(self):
        # Play song
        self.playAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
                self, shortcut="Ctrl+P", enabled=False, # when selected, disable function on UI to indicate it is already in use (button faded)
                triggered=self.mediaObject.play)

        # Pause song
        self.pauseAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
                "Pause", self, shortcut="Ctrl+A", enabled=False, # when selected, disable function on UI to indicate it is already in use (button faded)
                triggered=self.mediaObject.pause)

        # Stop song
        self.stopAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
                self, shortcut="Ctrl+S", enabled=False, # when selected, disable function on UI to indicate it is already in use (button faded)
                triggered=self.mediaObject.stop)

        # Skip to the next song in the playlist
        self.nextAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipForward),
                "Next", self, shortcut="Ctrl+N",enabled=True, # function is kept enabled on UI to indicate that it can be selected again
                triggered=self.next)

        # Go back to the last song in the playlist
        self.previousAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_MediaSkipBackward),
                "Previous", self, shortcut="Ctrl+R",enabled=True,  # function is kept enabled on UI to indicate that it can be selected again
                triggered=self.previous)

        # Add song to playlist
        self.addFilesAction = QtGui.QAction("Add Files", self,
                shortcut="Ctrl+F", triggered=self.addFiles)

        # Exit player
        self.exitAction = QtGui.QAction("Exit", self, shortcut="Ctrl+X",
                triggered=self.close)

        # Shuffle songs
        self.shuffleAction = QtGui.QAction(
                self.style().standardIcon(QtGui.QStyle.SP_BrowserReload),
                "Shuffle",self, shortcut="Ctrl+H",enabled=True,  # function is kept enabled on UI to indicate that it can be selected again
                triggered=self.shuffleSongs)

    #The shuffling engine was tricky. But we got it to work. It uses a simple random shuffler that is built in to ython. 
    #The songs are all attached to a list. Shuffling was the easy part. The tricky part was remapping the shuffled list back into the GUI. 
    #Calling self.setupUi will reset the GUI and take down all songs. Then the setCurrentSource commands will remap the shuffled list back into the table.
    def shuffleSongs(self):
        self.setupUi() # set up a "new" UI
        shuffle(self.sources) # shuffle the playlist
        
        self.metaInformationResolver.setCurrentSource(self.sources[0]) # set meta data finder to find meta data of first song of the playlist
        self.mediaObject.setCurrentSource(self.sources[0]) # set the first song of the playlist as the current song

        self.mediaObject.play() # play the playlist
        
    #Next and Previous functions. Stop currently playing music, go one forward or one back in the list, and play the song 
    #If the list is at the end, it will loop back to the start.
    def next(self):
        self.mediaObject.stop() # stop the current song
        self.mediaObject.clearQueue() # clear the queue
        index = self.sources.index(self.mediaObject.currentSource()) + 1 # index of the next song of the playlist
        try:
            self.mediaObject.setCurrentSource(self.sources[index]) # set the next song of the playlist to be the current
        except:
            self.mediaObject.setCurrentSource(self.sources[0]) # if the player cannot, set the first song of the playlist to be the current
            
        self.mediaObject.play() # play the song

    def previous(self):
        self.mediaObject.stop() # stop the current song
        self.mediaObject.clearQueue() # clear the queue
        index = self.sources.index(self.mediaObject.currentSource()) - 1 # index of the previous song of the playlist
        try:
            self.mediaObject.setCurrentSource(self.sources[index]) # set the previous song of the playlist to be the current 
            self.mediaObject.play # play the song
        except:
            self.mediaObject.setCurrentSource(self.sources[0]) # if the player cannot, set the first song of the playlist to be the current
        
        self.mediaObject.play()

    # Menu bar
    def setupMenuBar(self):
        fileMenu = self.menuBar().addMenu("&File") # add "File"
        fileMenu.addAction(self.addFilesAction) # add "Add Files"
        fileMenu.addSeparator() # separator
        fileMenu.addAction(self.exitAction) # add "Exit"

    # User Interface
    def setupUi(self):
        # play/pause/stop toolbar
        ppsbar = QtGui.QToolBar()
        ppsbar.addAction(self.playAction)  # add "Play"
        ppsbar.addAction(self.pauseAction) # add "Pause"
        ppsbar.addAction(self.stopAction) # add "Stop"
        ppsbar.addAction(self.previousAction) # add "Previous"
        ppsbar.addAction(self.nextAction) # add "Next"
        ppsbar.addAction(self.shuffleAction) # add "Shuffle"

        # volume icon
        volumeIcon = QtGui.QLabel()
        volumeIcon.setPixmap(QtGui.QPixmap('images/volume.png'))
        
        # volume slider
        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                QtGui.QSizePolicy.Maximum)
        
        # seek slider
        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)

        palette = QtGui.QPalette() # palette of music player
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray) # color scheme

        self.timeLcd = QtGui.QLCDNumber() # time display
        self.timeLcd.setPalette(palette) # color scheme

        headers = ("Title", "Artist", "Album", "Year") # table headers

        # table
        self.musicTable = QtGui.QTableWidget(0, 4)
        self.musicTable.setHorizontalHeaderLabels(headers) # headers
        self.musicTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection) # selection
        self.musicTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows) # selection behavior
        self.musicTable.cellPressed.connect(self.tableSelected) # table selected

        # seek layout
        seekLayout = QtGui.QHBoxLayout()
        seekLayout.addWidget(self.seekSlider) # seek slider
        seekLayout.addWidget(self.timeLcd) # time display

        # actions layout
        actionsLayout = QtGui.QHBoxLayout()
        actionsLayout.addWidget(ppsbar) # play/pause/stop toolbar
        actionsLayout.addStretch() # stretch
        actionsLayout.addWidget(volumeIcon) # volume icon
        actionsLayout.addWidget(self.volumeSlider) # volume slider

        # main layout (combine layouts)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.musicTable) # table
        mainLayout.addLayout(seekLayout) # seek layout
        mainLayout.addLayout(actionsLayout) # actions layout

        widget = QtGui.QWidget()
        widget.setLayout(mainLayout) # combine layouts on top of widget
        self.setCentralWidget(widget)
        self.setWindowTitle("Media Player") # window title

    #Defines the size of the UI
    def sizeHint(self):
        return QtCore.QSize(500, 300)

    #This is the function that creates the add files option on the menu at the top of the UI
    #Any songs added through this function will automatically be mapped on the table
    def addFiles(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Add Files",
                QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MusicLocation)) # open file browser

        if not files:
            return

        index = len(self.sources)

        for string in files:
            self.sources.append(Phonon.MediaSource(string))

        if self.sources:
            self.metaInformationResolver.setCurrentSource(self.sources[index])

    #This function simply changes how each button looks.
    #If a song is playing, the play button will look faded and the pause and stop
    def stateChanged(self, newState, oldState):
        if newState == Phonon.PlayingState: # if new state is "play"
            self.playAction.setEnabled(False) # disable play action
            self.pauseAction.setEnabled(True) # enable pause action
            self.stopAction.setEnabled(True) # enable stop action

        elif newState == Phonon.PausedState: # if new state is "pause"
            self.pauseAction.setEnabled(False) # disable pause action
            self.stopAction.setEnabled(True) # enable stop action
            self.playAction.setEnabled(True) # enable play action

        elif newState == Phonon.StoppedState: # if new state is "stop"
            self.stopAction.setEnabled(False) # disable stop action
            self.playAction.setEnabled(True) # enable play action
            self.pauseAction.setEnabled(False) # disable pause action
            self.timeLcd.display("00:00") # restart time display

    #This function creates the timer for the songs that is seen on the right sidebar
    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))
        
    #This function gives the ability to select a song by clicking on the table
    def tableSelected(self, row, column):
        self.mediaObject.stop() # stop current song
        self.mediaObject.clearQueue() # clear queue

        self.mediaObject.setCurrentSource(self.sources[row]) # set selection to current

        wasPlaying = (self.mediaObject.state() == Phonon.PlayingState)
        
        if wasPlaying:
            self.mediaObject.play()
        else:
            self.mediaObject.stop()

    #This function will queue a next song for the engine to compute when the current song is less than 10 seconds from finishing
    def aboutToFinish(self):
        index = self.sources.index(self.mediaObject.currentSource()) + 1 # index of next song
        if len(self.sources) > index:
            self.mediaObject.enqueue(self.sources[index])
        else:
            self.mediaObject.enqueue(self.sources[0]) 

    #If the song is changed, highlight the correct song on the table and reset the timer
    def sourceChanged(self, source):
        self.musicTable.selectRow(self.sources.index(source))
        self.timeLcd.display('00:00')

    #This function is part of the main functionality to extract ID3 tags and sample rate from each file. 
    #When a new song is placed onto the map, this function will gather the Title, Artist, Album, and Year of the song in question.
    #As an added bonus, the metaInformationResolver also automatically adjusts for a difference in sample rate. (We had an issue with that in previous versions)
    def metaStateChanged(self, newState, oldState):
        if newState != Phonon.StoppedState and newState != Phonon.PausedState:
            return

        if self.metaInformationResolver.currentSource().type() == Phonon.MediaSource.Invalid:
            return

        metaData = self.metaInformationResolver.metaData() # file's meta data

        # song's title
        title = metaData.get('TITLE', [''])[0] # retrieve title from meta data
        if not title: # if cannot be found
            title = self.metaInformationResolver.currentSource().fileName() # retrieve file name
        titleItem = QtGui.QTableWidgetItem(title)
        titleItem.setFlags(titleItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # song's artist
        artist = metaData.get('ARTIST', [''])[0] # retrieve artist from meta data
        artistItem = QtGui.QTableWidgetItem(artist)
        artistItem.setFlags(artistItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # song's album
        album = metaData.get('ALBUM', [''])[0] # retrieve album from meta data
        albumItem = QtGui.QTableWidgetItem(album)
        albumItem.setFlags(albumItem.flags() ^ QtCore.Qt.ItemIsEditable)

        # song's year
        year = metaData.get('YEAR', [''])[0] # retrieve year from meta data
        yearItem = QtGui.QTableWidgetItem(year)
        yearItem.setFlags(yearItem.flags() ^ QtCore.Qt.ItemIsEditable)

        currentRow = self.musicTable.rowCount() # row in table
        self.musicTable.insertRow(currentRow) # insert row
        self.musicTable.setItem(currentRow, 0, titleItem) # set title
        self.musicTable.setItem(currentRow, 1, artistItem) # set artist
        self.musicTable.setItem(currentRow, 2, albumItem) # set album
        self.musicTable.setItem(currentRow, 3, yearItem) # set year

        if not self.musicTable.selectedItems():
            self.musicTable.selectRow(0)
            self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        index = self.sources.index(self.metaInformationResolver.currentSource()) + 1

        if len(self.sources) > index:
            self.metaInformationResolver.setCurrentSource(self.sources[index])
        else:
            self.musicTable.resizeColumnsToContents()
            if self.musicTable.columnWidth(0) > 300:
                self.musicTable.setColumnWidth(0, 300)

#Main clause. Makes this py file executable.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Jukebox")
    app.setQuitOnLastWindowClosed(True)
    window = MediaPlayer()
    window.show()
    sys.exit(app.exec_())
