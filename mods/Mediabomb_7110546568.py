# ba_meta require api 9

from __future__ import annotations
from typing import TYPE_CHECKING

import time
import os
import random
import math
import json
import threading
import socket
import hashlib

import babase
import bauiv1 as bui
import bascenev1 as bs
import _babase
data_path_models = os.path.join("ba_data", "meshes" + os.sep)
data_path_textures = os.path.join("ba_data", "textures" + os.sep)
data_path_audio = os.path.join("ba_data", "audio" + os.sep)
mods_folder = _babase.env()['python_directory_user'] + os.sep

enable_ip_check = True

""" add ip address here so plugin will download files from this ip regardless of enable_ip_check value """
ip_whitelist = [
    'some good ip',
]

master_server = ('194.67.125.2', 45000)

def check_server_ip(ip_address, sock):
    if not enable_ip_check or ip_address in ip_whitelist:
        return True
    sock.settimeout(0.1)
    sock.sendto(('check' + ip_address[0]).encode('utf-8'), master_server)
    for i in range(5):
        data = None
        try:
            data, addr = sock.recvfrom(256)
        except:
            pass
        if data:
            if addr == master_server:
                if data == b'yes' + ip_address[0].encode('utf-8'):
                    return True
    return False

data_packet_len = 240
packets_per_fragment = 200
max_download_time = 120

protected_files = [
    'achievement.ogg', 'activateBeep.ogg', 'agent1.ogg', 'agent2.ogg', 'agent3.ogg', 'agent4.ogg', 'agentDeath.ogg', 'agentFall.ogg', 'agentHit1.ogg', 'agentHit2.ogg', 'alarm.ogg', 'ali1.ogg', 'ali2.ogg', 'ali3.ogg', 'ali4.ogg', 'aliDeath.ogg', 'aliFall.ogg', 'aliHit1.ogg', 'aliHit2.ogg',
    'announceEight.ogg', 'announceFive.ogg', 'announceFour.ogg', 'announceNine.ogg', 'announceOne.ogg', 'announceSeven.ogg', 'announceSix.ogg', 'announceTen.ogg', 'announceThree.ogg', 'announceTwo.ogg', 'bear1.ogg', 'bear2.ogg', 'bear3.ogg', 'bear4.ogg', 'bearDeath.ogg', 'bearFall.ogg',
    'bearHit1.ogg', 'bearHit2.ogg', 'bellHigh.ogg', 'bellLow.ogg', 'bellMed.ogg', 'bigImpact.ogg', 'bigImpact2.ogg', 'blank.ogg', 'blip.ogg', 'block.ogg', 'bombDrop01.ogg', 'bombDrop02.ogg', 'bombRoll01.ogg', 'bones1.ogg', 'bones2.ogg', 'bones3.ogg', 'bonesDeath.ogg', 'bonesFall.ogg', 'boo.ogg',
    'boxDrop.ogg', 'boxingBell.ogg', 'bunny1.ogg', 'bunny2.ogg', 'bunny3.ogg', 'bunny4.ogg', 'bunnyDeath.ogg', 'bunnyFall.ogg', 'bunnyHit1.ogg', 'bunnyHit2.ogg', 'bunnyJump.ogg', 'cashRegister.ogg', 'cashRegister2.ogg', 'charSelectMusic.ogg', 'cheer.ogg', 'click01.ogg', 'corkPop.ogg',
    'crowdChant.ogg', 'cyborg1.ogg', 'cyborg2.ogg', 'cyborg3.ogg', 'cyborg4.ogg', 'cyborgDeath.ogg', 'cyborgFall.ogg', 'cyborgHit1.ogg', 'cyborgHit2.ogg', 'cymbal.ogg', 'debrisFall.ogg', 'deek.ogg', 'deek2.ogg', 'ding.ogg', 'dingSmall.ogg', 'dingSmallHigh.ogg', 'dripity.ogg', 'drumRoll.ogg',
    'error.ogg', 'explosion01.ogg', 'explosion02.ogg', 'explosion03.ogg', 'explosion04.ogg', 'explosion05.ogg', 'fanfare.ogg', 'flagCatcherMusic.ogg', 'flyingMusic.ogg', 'foghorn.ogg', 'footImpact01.ogg', 'footImpact02.ogg', 'footImpact03.ogg', 'forwardMarchMusic.ogg', 'freeze.ogg', 'frosty01.ogg',
    'frosty02.ogg', 'frosty03.ogg', 'frosty04.ogg', 'frosty05.ogg', 'frostyDeath.ogg', 'frostyFall.ogg', 'frostyHit01.ogg', 'frostyHit02.ogg', 'frostyHit03.ogg', 'fuse01.ogg', 'gong.ogg', 'grandRompMusic.ogg', 'gravelSkid.ogg', 'gunCocking.ogg', 'healthPowerup.ogg', 'hiss.ogg', 'impactHard.ogg',
    'impactHard2.ogg', 'impactHard3.ogg', 'impactMedium.ogg', 'impactMedium2.ogg', 'jack01.ogg', 'jack02.ogg', 'jack03.ogg', 'jack04.ogg', 'jack05.ogg', 'jack06.ogg', 'jackDeath01.ogg', 'jackFall01.ogg', 'jackHit01.ogg', 'jackHit02.ogg', 'jackHit03.ogg', 'jackHit04.ogg', 'jackHit05.ogg',
    'jackHit06.ogg', 'jackHit07.ogg', 'kronk1.ogg', 'kronk10.ogg', 'kronk2.ogg', 'kronk3.ogg', 'kronk4.ogg', 'kronk5.ogg', 'kronk6.ogg', 'kronk7.ogg', 'kronk8.ogg', 'kronk9.ogg', 'kronkDeath.ogg', 'kronkFall.ogg', 'laser.ogg', 'laserReverse.ogg', 'mel01.ogg', 'mel02.ogg', 'mel03.ogg', 'mel04.ogg',
    'mel05.ogg', 'mel06.ogg', 'mel07.ogg', 'mel08.ogg', 'mel09.ogg', 'mel10.ogg', 'melDeath01.ogg', 'melFall01.ogg', 'menuMusic.ogg', 'metalHit.ogg', 'metalSkid.ogg', 'ninjaAttack1.ogg', 'ninjaAttack2.ogg', 'ninjaAttack3.ogg', 'ninjaAttack4.ogg', 'ninjaAttack5.ogg', 'ninjaAttack6.ogg',
    'ninjaAttack7.ogg', 'ninjaDeath1.ogg', 'ninjaFall1.ogg', 'ninjaHit1.ogg', 'ninjaHit2.ogg', 'ninjaHit3.ogg', 'ninjaHit4.ogg', 'ninjaHit5.ogg', 'ninjaHit6.ogg', 'ninjaHit7.ogg', 'ninjaHit8.ogg', 'ooh.ogg', 'orchestraHit.ogg', 'orchestraHit2.ogg', 'orchestraHit3.ogg', 'orchestraHit4.ogg',
    'orchestraHitBig1.ogg', 'orchestraHitBig2.ogg', 'penguin1.ogg', 'penguin2.ogg', 'penguin3.ogg', 'penguin4.ogg', 'penguinDeath.ogg', 'penguinFall.ogg', 'penguinHit1.ogg', 'penguinHit2.ogg', 'pixie1.ogg', 'pixie2.ogg', 'pixie3.ogg', 'pixie4.ogg', 'pixieDeath.ogg', 'pixieFall.ogg',
    'pixieHit1.ogg', 'pixieHit2.ogg', 'playerDeath.ogg', 'playerLeft.ogg', 'pop01.ogg', 'powerdown01.ogg', 'powerup01.ogg', 'punch01.ogg', 'punchStrong01.ogg', 'punchStrong02.ogg', 'punchSwish.ogg', 'punchWeak01.ogg', 'raceBeep1.ogg', 'raceBeep2.ogg', 'refWhistle.ogg', 'runAwayMusic.ogg',
    'santa01.ogg', 'santa02.ogg', 'santa03.ogg', 'santa04.ogg', 'santa05.ogg', 'santaDeath.ogg', 'santaFall.ogg', 'santaHit01.ogg', 'santaHit02.ogg', 'santaHit03.ogg', 'santaHit04.ogg', 'scamper01.ogg', 'scaryMusic.ogg', 'score.ogg', 'scoreHit01.ogg', 'scoreHit02.ogg', 'scoreIncrease.ogg',
    'scoresEpicMusic.ogg', 'shatter.ogg', 'shieldDown.ogg', 'shieldHit.ogg', 'shieldUp.ogg', 'skid01.ogg', 'slowEpicMusic.ogg', 'sparkle01.ogg', 'sparkle02.ogg', 'sparkle03.ogg', 'spawn.ogg', 'spazAttack01.ogg', 'spazAttack02.ogg', 'spazAttack03.ogg', 'spazAttack04.ogg', 'spazDeath01.ogg',
    'spazEff.ogg', 'spazFall01.ogg', 'spazImpact01.ogg', 'spazImpact02.ogg', 'spazImpact03.ogg', 'spazImpact04.ogg', 'spazJump01.ogg', 'spazJump02.ogg', 'spazJump03.ogg', 'spazJump04.ogg', 'spazOw.ogg', 'spazPickup01.ogg', 'spazScream01.ogg', 'splatter.ogg', 'sportsMusic.ogg', 'stickyImpact.ogg',
    'superPunch.ogg', 'survivalMusic.ogg', 'swip.ogg', 'swip2.ogg', 'swish.ogg', 'swish2.ogg', 'swish3.ogg', 'tap.ogg', 'technoHit01.ogg', 'tick.ogg', 'ticking.ogg', 'tickingCrazy.ogg', 'toTheDeathMusic.ogg', 'trashRummage.ogg', 'victoryMusic.ogg', 'warnBeep.ogg', 'warnBeeps.ogg',
    'whenJohnnyComesMarchingHomeMusic.ogg', 'wizard1.ogg', 'wizard2.ogg', 'wizard3.ogg', 'wizard4.ogg', 'wizardDeath.ogg', 'wizardFall.ogg', 'wizardHit1.ogg', 'wizardHit2.ogg', 'woodDebrisFall.ogg', 'ZhitikaraBallSound.ogg', 'zoeAttack01.ogg', 'zoeAttack02.ogg', 'zoeAttack03.ogg',
    'zoeAttack04.ogg', 'zoeDeath01.ogg', 'zoeEff.ogg', 'zoeFall01.ogg', 'zoeImpact01.ogg', 'zoeImpact02.ogg', 'zoeImpact03.ogg', 'zoeImpact04.ogg', 'zoeJump01.ogg', 'zoeJump02.ogg', 'zoeJump03.ogg', 'zoeOw.ogg', 'zoePickup01.ogg', 'zoeScream01.ogg', 'achievementOutline.bob',
    'actionButtonBottom.bob', 'actionButtonLeft.bob', 'actionButtonRight.bob', 'actionButtonTop.bob', 'agentForeArm.bob', 'agentHand.bob', 'agentHead.bob', 'agentLowerLeg.bob', 'agentPelvis.bob', 'agentToes.bob', 'agentTorso.bob', 'agentUpperArm.bob', 'agentUpperLeg.bob', 'aliForeArm.bob',
    'aliHand.bob', 'aliHead.bob', 'aliLowerLeg.bob', 'aliPelvis.bob', 'aliToes.bob', 'aliTorso.bob', 'aliUpperArm.bob', 'aliUpperLeg.bob', 'alwaysLandBG.bob', 'alwaysLandLevel.bob', 'alwaysLandLevelBottom.bob', 'alwaysLandLevelCollide.cob', 'alwaysLandVRFillMound.bob',
    'angryComputerTransparent.bob', 'arrowBack.bob', 'arrowFront.bob', 'bearForeArm.bob', 'bearHand.bob', 'bearHead.bob', 'bearLowerLeg.bob', 'bearPelvis.bob', 'bearToes.bob', 'bearTorso.bob', 'bearUpperArm.bob', 'bearUpperLeg.bob', 'bigG.bob', 'bigGBottom.bob', 'bigGBumper.cob', 'bigGCollide.cob',
    'bomb.bob', 'bombSticky.bob', 'bonesForeArm.bob', 'bonesHand.bob', 'bonesHead.bob', 'bonesLowerLeg.bob', 'bonesPelvis.bob', 'bonesToes.bob', 'bonesTorso.bob', 'bonesUpperArm.bob', 'bonesUpperLeg.bob', 'box.bob', 'boxingGlove.bob', 'bridgitLevelBottom.bob', 'bridgitLevelCollide.cob',
    'bridgitLevelRailingCollide.cob', 'bridgitLevelTop.bob', 'bunnyForeArm.bob', 'bunnyHand.bob', 'bunnyHead.bob', 'bunnyLowerLeg.bob', 'bunnyPelvis.bob', 'bunnyToes.bob', 'bunnyTorso.bob', 'bunnyUpperArm.bob', 'bunnyUpperLeg.bob', 'buttonBackOpaque.bob', 'buttonBackSmallOpaque.bob',
    'buttonBackSmallTransparent.bob', 'buttonBackTransparent.bob', 'buttonLargeOpaque.bob', 'buttonLargerOpaque.bob', 'buttonLargerTransparent.bob', 'buttonLargeTransparent.bob', 'buttonMediumOpaque.bob', 'buttonMediumTransparent.bob', 'buttonNull.bob', 'buttonSmallOpaque.bob',
    'buttonSmallTransparent.bob', 'buttonSquareOpaque.bob', 'buttonSquareTransparent.bob', 'buttonTabOpaque.bob', 'buttonTabTransparent.bob', 'checkTransparent.bob', 'courtyardLevel.bob', 'courtyardLevelBottom.bob', 'courtyardLevelCollide.cob', 'courtyardPlayerWall.cob', 'cragCastleLevel.bob',
    'cragCastleLevelBottom.bob', 'cragCastleLevelBumper.cob', 'cragCastleLevelCollide.cob', 'cragCastleVRFillMound.bob', 'crossOut.bob', 'currencyMeter.bob', 'currencyPlusButton.bob', 'cyborgForeArm.bob', 'cyborgHand.bob', 'cyborgHead.bob', 'cyborgLowerLeg.bob', 'cyborgPelvis.bob',
    'cyborgToes.bob', 'cyborgTorso.bob', 'cyborgUpperArm.bob', 'cyborgUpperLeg.bob', 'cylinder.bob', 'doomShroomBG.bob', 'doomShroomLevel.bob', 'doomShroomLevelCollide.cob', 'doomShroomStem.bob', 'doomShroomStemCollide.cob', 'doomShroomVRFill.bob', 'egg.bob', 'eyeBall.bob', 'eyeBallIris.bob',
    'eyeLid.bob', 'flagPole.bob', 'flagStand.bob', 'flash.bob', 'footballStadium.bob', 'footballStadiumCollide.cob', 'footballStadiumVRFill.bob', 'frameInset.bob', 'frostyForeArm.bob', 'frostyHand.bob', 'frostyHead.bob', 'frostyLowerLeg.bob', 'frostyPelvis.bob', 'frostyToes.bob', 'frostyTorso.bob',
    'frostyUpperArm.bob', 'frostyUpperLeg.bob', 'hairTuft1.bob', 'hairTuft1b.bob', 'hairTuft2.bob', 'hairTuft3.bob', 'hairTuft4.bob', 'heartOpaque.bob', 'heartTransparent.bob', 'hockeyStadiumCollide.cob', 'hockeyStadiumInner.bob', 'hockeyStadiumOuter.bob', 'hockeyStadiumStands.bob',
    'image16x1.bob', 'image1x1.bob', 'image1x1FullScreen.bob', 'image1x1VRFullScreen.bob', 'image2x1.bob', 'image2x1Vertical.bob', 'image4x1.bob', 'impactBomb.bob', 'jackForeArm.bob', 'jackHand.bob', 'jackHead.bob', 'jackLowerLeg.bob', 'jackToes.bob', 'jackTorso.bob', 'jackUpperArm.bob',
    'jackUpperLeg.bob', 'kronkForeArm.bob', 'kronkHand.bob', 'kronkHead.bob', 'kronkLowerLeg.bob', 'kronkPelvis.bob', 'kronkToes.bob', 'kronkTorso.bob', 'kronkUpperArm.bob', 'kronkUpperLeg.bob', 'lakeFrigid.bob', 'lakeFrigidCollide.cob', 'lakeFrigidReflections.bob', 'lakeFrigidTop.bob',
    'lakeFrigidVRFill.bob', 'landMine.bob', 'level_select_button_opaque.bob', 'level_select_button_transparent.bob', 'locator.bob', 'locatorBox.bob', 'locatorCircle.bob', 'locatorCircleOutline.bob', 'logo.bob', 'logoTransparent.bob', 'melForeArm.bob', 'melHand.bob', 'melHead.bob',
    'melLowerLeg.bob', 'melToes.bob', 'melTorso.bob', 'melUpperArm.bob', 'melUpperLeg.bob', 'meterTransparent.bob', 'monkeyFaceLevel.bob', 'monkeyFaceLevelBottom.bob', 'monkeyFaceLevelBumper.cob', 'monkeyFaceLevelCollide.cob', 'natureBackground.bob', 'natureBackgroundCollide.cob',
    'natureBackgroundVRFill.bob', 'neoSpazForeArm.bob', 'neoSpazHand.bob', 'neoSpazHead.bob', 'neoSpazLowerLeg.bob', 'neoSpazPelvis.bob', 'neoSpazToes.bob', 'neoSpazTorso.bob', 'neoSpazUpperArm.bob', 'neoSpazUpperLeg.bob', 'ninjaForeArm.bob', 'ninjaHand.bob', 'ninjaHead.bob', 'ninjaLowerLeg.bob',
    'ninjaPelvis.bob', 'ninjaToes.bob', 'ninjaTorso.bob', 'ninjaUpperArm.bob', 'ninjaUpperLeg.bob', 'overlayGuide.bob', 'penguinForeArm.bob', 'penguinHand.bob', 'penguinHead.bob', 'penguinLowerLeg.bob', 'penguinPelvis.bob', 'penguinToes.bob', 'penguinTorso.bob', 'penguinUpperArm.bob',
    'penguinUpperLeg.bob', 'pixieForeArm.bob', 'pixieHand.bob', 'pixieHead.bob', 'pixieLowerLeg.bob', 'pixiePelvis.bob', 'pixieToes.bob', 'pixieTorso.bob', 'pixieUpperArm.bob', 'pixieUpperLeg.bob', 'plasticEyesTransparent.bob', 'playerLineup1Transparent.bob', 'playerLineup2Transparent.bob',
    'playerLineup3Transparent.bob', 'playerLineup4Transparent.bob', 'powerup.bob', 'powerupSimple.bob', 'puck.bob', 'rampageBG.bob', 'rampageBG2.bob', 'rampageBumper.cob', 'rampageLevel.bob', 'rampageLevelBottom.bob', 'rampageLevelCollide.cob', 'rampageVRFill.bob', 'roundaboutLevel.bob',
    'roundaboutLevelBottom.bob', 'roundaboutLevelBumper.cob', 'roundaboutLevelCollide.cob', 'runningShoes.bob', 'santaForeArm.bob', 'santaHand.bob', 'santaHead.bob', 'santaLowerLeg.bob', 'santaToes.bob', 'santaTorso.bob', 'santaUpperArm.bob', 'santaUpperLeg.bob', 'scorch.bob',
    'scrollBarThumbOpaque.bob', 'scrollBarThumbShortOpaque.bob', 'scrollBarThumbShortSimple.bob', 'scrollBarThumbShortTransparent.bob', 'scrollBarThumbSimple.bob', 'scrollBarThumbTransparent.bob', 'scrollBarTroughTransparent.bob', 'scrollWidgetShort.bob', 'shield.bob', 'shockWave.bob',
    'shrapnel1.bob', 'shrapnelBoard.bob', 'shrapnelSlime.bob', 'softEdgeInside.bob', 'softEdgeOutside.bob', 'stepRightUpLevel.bob', 'stepRightUpLevelBottom.bob', 'stepRightUpLevelCollide.cob', 'stepRightUpVRFillMound.bob', 'textBoxTransparent.bob', 'thePadBG.bob', 'thePadBGSmall.bob',
    'thePadLevel.bob', 'thePadLevelBottom.bob', 'thePadLevelBumper.cob', 'thePadLevelCollide.cob', 'thePadVRFillBottom.bob', 'thePadVRFillMound.bob', 'thePadVRFillTop.bob', 'tipTopBG.bob', 'tipTopLevel.bob', 'tipTopLevelBottom.bob', 'tipTopLevelBumper.cob', 'tipTopLevelCollide.cob', 'tnt.bob',
    'toolbarBacking.bob', 'toolbarBackingBottom.bob', 'toolbarBackingBottom2.bob', 'toolbarBackingOpaque.bob', 'toolbarBackingTop.bob', 'toolbarBackingTop2.bob', 'toolbarBackingTransparent.bob', 'towerDLevel.bob', 'towerDLevelBottom.bob', 'towerDLevelCollide.cob', 'towerDPlayerWall.cob',
    'trees.bob', 'vrFade.bob', 'vrOverlay.bob', 'windowBGBlotch.bob', 'windowHSmallVMedOpaque.bob', 'windowHSmallVMedTransparent.bob', 'windowHSmallVSmallOpaque.bob', 'windowHSmallVSmallTransparent.bob', 'wing.bob', 'wizardForeArm.bob', 'wizardHand.bob', 'wizardHead.bob', 'wizardLowerLeg.bob',
    'wizardPelvis.bob', 'wizardToes.bob', 'wizardTorso.bob', 'wizardUpperArm.bob', 'wizardUpperLeg.bob', 'ZhitikaraBall.bob', 'zigZagLevel.bob', 'zigZagLevelBottom.bob', 'zigZagLevelBumper.cob', 'zigZagLevelCollide.cob', 'zoeForeArm.bob', 'zoeHand.bob', 'zoeHead.bob', 'zoeLowerLeg.bob',
    'zoePelvis.bob', 'zoeToes.bob', 'zoeTorso.bob', 'zoeUpperArm.bob', 'zoeUpperLeg.bob', 'achievementBoxer.dds', 'achievementCrossHair.dds', 'achievementDualWielding.dds', 'achievementEmpty.dds', 'achievementFlawlessVictory.dds', 'achievementFootballShutout.dds', 'achievementFootballVictory.dds',
    'achievementFreeLoader.dds', 'achievementGotTheMoves.dds', 'achievementInControl.dds', 'achievementMedalLarge.dds', 'achievementMedalMedium.dds', 'achievementMedalSmall.dds', 'achievementMine.dds', 'achievementOffYouGo.dds', 'achievementOnslaught.dds', 'achievementOutline.dds',
    'achievementRunaround.dds', 'achievementSharingIsCaring.dds', 'achievementsIcon.dds', 'achievementStayinAlive.dds', 'achievementSuperPunch.dds', 'achievementTeamPlayer.dds', 'achievementTNT.dds', 'achievementWall.dds', 'actionButtons.dds', 'advancedIcon.dds', 'agentColor.dds',
    'agentColorMask.dds', 'agentIcon.dds', 'agentIconColorMask.dds', 'aliBSRemoteIOSQR.dds', 'aliColor.dds', 'aliColorMask.dds', 'aliControllerQR.dds', 'aliIcon.dds', 'aliIconColorMask.dds', 'aliSplash.dds', 'alwaysLandBGColor.dds', 'alwaysLandLevelColor.dds', 'alwaysLandPreview.dds',
    'analogStick.dds', 'arrow.dds', 'audioIcon.dds', 'backIcon.dds', 'bar.dds', 'bearColor.dds', 'bearColorMask.dds', 'bearIcon.dds', 'bearIconColorMask.dds', 'bg.dds', 'bigG.dds', 'bigGPreview.dds', 'black.dds', 'bombButton.dds', 'bombColor.dds', 'bombColorIce.dds', 'bombStickyColor.dds',
    'bonesColor.dds', 'bonesColorMask.dds', 'bonesIcon.dds', 'bonesIconColorMask.dds', 'boxingGlovesColor.dds', 'bridgitLevelColor.dds', 'bridgitPreview.dds', 'bunnyColor.dds', 'bunnyColorMask.dds', 'bunnyIcon.dds', 'bunnyIconColorMask.dds', 'buttonBomb.dds', 'buttonJump.dds', 'buttonPickUp.dds',
    'buttonPunch.dds', 'buttonSquare.dds', 'characterIconMask.dds', 'chestIcon.dds', 'chestIconEmpty.dds', 'chestIconMulti.dds', 'chestOpenIcon.dds', 'chTitleChar1.dds', 'chTitleChar2.dds', 'chTitleChar3.dds', 'chTitleChar4.dds', 'chTitleChar5.dds', 'circle.dds', 'circleNoAlpha.dds',
    'circleOutline.dds', 'circleOutlineNoAlpha.dds', 'circleShadow.dds', 'circleZigZag.dds', 'coin.dds', 'controllerIcon.dds', 'courtyardLevelColor.dds', 'courtyardPreview.dds', 'cragCastleLevelColor.dds', 'cragCastlePreview.dds', 'crossOut.dds', 'crossOutMask.dds', 'cursor.dds', 'cuteSpaz.dds',
    'cyborgColor.dds', 'cyborgColorMask.dds', 'cyborgIcon.dds', 'cyborgIconColorMask.dds', 'discordLogo.dds', 'discordServer.dds', 'doomShroomBGColor.dds', 'doomShroomLevelColor.dds', 'doomShroomPreview.dds', 'downButton.dds', 'egg1.dds', 'egg2.dds', 'egg3.dds', 'egg4.dds', 'eggTex1.dds',
    'eggTex2.dds', 'eggTex3.dds', 'empty.dds', 'explosion.dds', 'eyeColor.dds', 'eyeColorTintMask.dds', 'file.dds', 'flagColor.dds', 'flagPoleColor.dds', 'folder.dds', 'fontBig.dds', 'fontExtras.dds', 'fontExtras2.dds', 'fontExtras3.dds', 'fontExtras4.dds', 'fontSmall0.dds', 'fontSmall1.dds',
    'fontSmall2.dds', 'fontSmall3.dds', 'fontSmall4.dds', 'fontSmall5.dds', 'fontSmall6.dds', 'fontSmall7.dds', 'footballStadium.dds', 'footballStadiumPreview.dds', 'frameInset.dds', 'frostyColor.dds', 'frostyColorMask.dds', 'frostyIcon.dds', 'frostyIconColorMask.dds', 'fuse.dds',
    'gameCenterIcon.dds', 'gameCircleIcon.dds', 'githubLogo.dds', 'glow.dds', 'googlePlayAchievementsIcon.dds', 'googlePlayGamesIcon.dds', 'googlePlayLeaderboardsIcon.dds', 'googlePlusIcon.dds', 'googlePlusSignInButton.dds', 'graphicsIcon.dds', 'heart.dds', 'hockeyStadium.dds',
    'hockeyStadiumPreview.dds', 'iconOnslaught.dds', 'iconRunaround.dds', 'iircadeLogo.dds', 'impactBombColor.dds', 'impactBombColorLit.dds', 'inventoryIcon.dds', 'jackColor.dds', 'jackColorMask.dds', 'jackIcon.dds', 'jackIconColorMask.dds', 'kronk.dds', 'kronkColorMask.dds', 'kronkIcon.dds',
    'kronkIconColorMask.dds', 'lakeFrigid.dds', 'lakeFrigidPreview.dds', 'lakeFrigidReflections.dds', 'landMine.dds', 'landMineLit.dds', 'leaderboardsIcon.dds', 'leftButton.dds', 'levelIcon.dds', 'light.dds', 'lightSharp.dds', 'lightSoft.dds', 'lock.dds', 'logIcon.dds', 'logo.dds',
    'logoEaster.dds', 'mapPreviewMask.dds', 'medalBronze.dds', 'medalComplete.dds', 'medalGold.dds', 'medalSilver.dds', 'melColor.dds', 'melColorMask.dds', 'melIcon.dds', 'melIconColorMask.dds', 'menuBG.dds', 'menuButton.dds', 'menuIcon.dds', 'meter.dds', 'monkeyFaceLevelColor.dds',
    'monkeyFacePreview.dds', 'multiplayerExamples.dds', 'natureBackgroundColor.dds', 'neoSpazColor.dds', 'neoSpazColorMask.dds', 'neoSpazIcon.dds', 'neoSpazIconColorMask.dds', 'nextLevelIcon.dds', 'ninjaColor.dds', 'ninjaColorMask.dds', 'ninjaIcon.dds', 'ninjaIconColorMask.dds', 'nub.dds',
    'null.dds', 'ouyaAButton.dds', 'ouyaIcon.dds', 'ouyaOButton.dds', 'ouyaUButton.dds', 'ouyaYButton.dds', 'penguinColor.dds', 'penguinColorMask.dds', 'penguinIcon.dds', 'penguinIconColorMask.dds', 'pixieColor.dds', 'pixieColorMask.dds', 'pixieIcon.dds', 'pixieIconColorMask.dds',
    'playerLineup.dds', 'powerupBomb.dds', 'powerupCurse.dds', 'powerupHealth.dds', 'powerupIceBombs.dds', 'powerupImpactBombs.dds', 'powerupLandMines.dds', 'powerupPunch.dds', 'powerupShield.dds', 'powerupSpeed.dds', 'powerupStickyBombs.dds', 'puckColor.dds', 'rampageBGColor.dds',
    'rampageBGColor2.dds', 'rampageLevelColor.dds', 'rampagePreview.dds', 'reflectionChar_+x.dds', 'reflectionChar_+y.dds', 'reflectionChar_+z.dds', 'reflectionChar_-x.dds', 'reflectionChar_-y.dds', 'reflectionChar_-z.dds', 'reflectionPowerup_+x.dds', 'reflectionPowerup_+y.dds',
    'reflectionPowerup_+z.dds', 'reflectionPowerup_-x.dds', 'reflectionPowerup_-y.dds', 'reflectionPowerup_-z.dds', 'reflectionSharper_+x.dds', 'reflectionSharper_+y.dds', 'reflectionSharper_+z.dds', 'reflectionSharper_-x.dds', 'reflectionSharper_-y.dds', 'reflectionSharper_-z.dds',
    'reflectionSharpest_+x.dds', 'reflectionSharpest_+y.dds', 'reflectionSharpest_+z.dds', 'reflectionSharpest_-x.dds', 'reflectionSharpest_-y.dds', 'reflectionSharpest_-z.dds', 'reflectionSharp_+x.dds', 'reflectionSharp_+y.dds', 'reflectionSharp_+z.dds', 'reflectionSharp_-x.dds',
    'reflectionSharp_-y.dds', 'reflectionSharp_-z.dds', 'reflectionSoft_+x.dds', 'reflectionSoft_+y.dds', 'reflectionSoft_+z.dds', 'reflectionSoft_-x.dds', 'reflectionSoft_-y.dds', 'reflectionSoft_-z.dds', 'replayIcon.dds', 'rgbStripes.dds', 'rightButton.dds', 'roundaboutLevelColor.dds',
    'roundaboutPreview.dds', 'santaColor.dds', 'santaColorMask.dds', 'santaIcon.dds', 'santaIconColorMask.dds', 'scorch.dds', 'scorchBig.dds', 'scrollWidget.dds', 'scrollWidgetGlow.dds', 'settingsIcon.dds', 'shadow.dds', 'shadowSharp.dds', 'shadowSoft.dds', 'shield.dds', 'shrapnel1Color.dds',
    'slash.dds', 'smoke.dds', 'softRect.dds', 'softRect2.dds', 'softRectVertical.dds', 'sparks.dds', 'star.dds', 'startButton.dds', 'stepRightUpLevelColor.dds', 'stepRightUpPreview.dds', 'storeCharacter.dds', 'storeCharacterEaster.dds', 'storeCharacterXmas.dds', 'storeIcon.dds',
    'textClearButton.dds', 'thePadLevelColor.dds', 'thePadPreview.dds', 'ticketRoll.dds', 'ticketRollBig.dds', 'ticketRolls.dds', 'tickets.dds', 'ticketsMore.dds', 'tipTopBGColor.dds', 'tipTopLevelColor.dds', 'tipTopPreview.dds', 'tnt.dds', 'touchArrows.dds', 'touchArrowsActions.dds',
    'towerDLevelColor.dds', 'towerDPreview.dds', 'treesColor.dds', 'trophy.dds', 'tv.dds', 'uiAtlas.dds', 'uiAtlas2.dds', 'upButton.dds', 'usersButton.dds', 'vrFillMound.dds', 'white.dds', 'windowHSmallVMed.dds', 'windowHSmallVSmall.dds', 'wings.dds', 'wizardColor.dds', 'wizardColorMask.dds',
]


def unpack_binary_file(filename_full):
    if not os.path.exists(filename_full):
        return None, None
    with open(filename_full, mode='rb') as f:
        file_bytes = f.read()
        file_hash = hashlib.md5(file_bytes).hexdigest()
        return file_bytes, file_hash
    return None, None

def check_file(filename, _hash):
    if filename.endswith('.bob') or filename.endswith('.cob'):
        file_bytes, file_hash = unpack_binary_file(data_path_models + filename)
        if file_hash == _hash:
            return True
    if filename.endswith('.dds') or filename.endswith('.ktx'):
        file_bytes, file_hash = unpack_binary_file(data_path_textures + filename)
        if file_hash == _hash:
            return True
    if filename.endswith('.ogg'):
        file_bytes, file_hash = unpack_binary_file(data_path_audio + filename)
        if file_hash == _hash:
            return True
    return False

def save_file_from_mods(filename, _hash):
    file_bytes, file_hash = unpack_binary_file(mods_folder + filename)
    if file_hash is not None:
        if file_hash == _hash:
            save_file(filename, file_bytes)
        os.remove(mods_folder + filename)
        return file_hash == _hash
    return False

def save_file(filename, file_bytes):
    if filename.endswith('.bob') or filename.endswith('.cob'):
        folder = data_path_models
    elif filename.endswith('.dds') or filename.endswith('.ktx'):
        folder = data_path_textures
    elif filename.endswith('.ogg'):
        folder = data_path_audio
    else:
        return False
    with open(folder + filename, mode='wb') as f:
        f.write(file_bytes)
        return True
    return False

def calculate_overall_hash(files_list):
    files_list.sort()
    long_str = ''
    for filename in files_list:
        if filename.endswith('.bob') or filename.endswith('.cob'):
            folder = data_path_models
        elif filename.endswith('.dds') or filename.endswith('.ktx'):
            folder = data_path_textures
        elif filename.endswith('.ogg'):
            folder = data_path_audio
        else:
            return ''
        file_bytes, file_hash = unpack_binary_file(folder + filename)
        if file_hash is not None:
            long_str += file_hash
    overall_hash = hashlib.md5(long_str.encode('utf-8')).hexdigest()
    return overall_hash


class DownloadFileFromServerThread(threading.Thread):

    def __init__(self, server_address, filename, file_data):
        super().__init__(daemon=True)
        self.server_address = server_address
        self.filename = filename
        self.file_data = file_data

        self.parts_to_get = 0
        self.parts_got = 0

    def run(self) -> None:
        self.start_time = time.time()
        self.end_time = self.start_time + max_download_time
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.1)
        if self.get_file_download_port():
            self.parts_to_get = (self.file_data['len'] - 1) // (data_packet_len * packets_per_fragment) + 1
            if self.get_file():
                pass
        self.socket.close()

    def get_file_download_port(self):
        while time.time() < self.start_time + 5:
            self.socket.sendto(b'getport:' + self.filename.encode('utf-8'), self.server_address)
            data = None
            for i in range(10):
                try:
                    data, addr = self.socket.recvfrom(256)
                except:
                    pass
                if data:
                    if addr == self.server_address:
                        if data.startswith(b'port:'):
                            try:
                                new_port = int(data[5:].decode('utf-8'))
                                if new_port < 65535:
                                    self.server_address = (self.server_address[0], new_port)
                                    return True
                            except:
                                pass
        return False

    def get_file(self):
        if save_file_from_mods(self.filename, self.file_data['hash']):
            self.parts_got = self.part_to_get
            return True
        last_packet_time = time.time()
        last_packet_time_2 = time.time()
        file_bytes = b''
        _part = -1
        _part_hash = None
        _part_len = 0
        _part_bytes = b''
        while time.time() < self.end_time:
            if self.parts_got == self.parts_to_get:
                break
            if _part < self.parts_got:
                _part = self.parts_got
                self.socket.sendto(b'filepart:' + str(_part).encode('utf-8'), self.server_address)
                last_packet_time = time.time()
                _part_hash = None
                _part_len = min(data_packet_len * packets_per_fragment * (_part + 1), self.file_data['len']) - data_packet_len * packets_per_fragment * _part
                _part_bytes = b''
                time.sleep(0.02)
            data = None
            try:
                data, addr = self.socket.recvfrom(256)
            except Exception:
                pass
            if data:
                if addr == self.server_address:
                    last_packet_time = time.time()
                    last_packet_time_2 = time.time()
                    if data.startswith(b'parthash'):
                        try:
                            if int(data[8:data.find(b':')].decode('utf-8')) == _part:
                                _part_hash = data[data.find(b':') + 1:].decode('utf-8')
                        except:
                            pass
                    elif _part_hash is not None:
                        _part_bytes += data
                        if len(_part_bytes) >= _part_len:
                            try_hash = hashlib.md5(_part_bytes).hexdigest()
                            if try_hash == _part_hash:
                                file_bytes += _part_bytes
                                self.parts_got += 1
                            else:
                                _part -= 1
            if last_packet_time_2 < time.time() - 10.0:
                break
            if last_packet_time < time.time() - 0.3:
                _part -= 1
        if self.parts_got == self.parts_to_get:
            if hashlib.md5(file_bytes).hexdigest() == self.file_data['hash']:
                if save_file(self.filename, file_bytes):
                    return True
        return False


class GetFilesThread(threading.Thread):

    def __init__(self, server_name, server_address, overall_hash):
        super().__init__(daemon=True)
        self.server_name = server_name
        self.server_address = server_address
        self.overall_hash = overall_hash
        self.files_list = {}
        self.status = 'not finished'
        self.files_saved = False

    def run(self) -> None:
        self.start_time = time.time()
        self.end_time = self.start_time + max_download_time
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(0.1)
        self.active_threads = []
        self.files_to_download = []
        if self.receive_files_list():
            if self.get_files():
                pass
        self.end_time = time.time()
        self.socket.close()

    def receive_files_list(self):
        import platform
        if platform.system() in ['Linux', 'Android']:
            platform_name = 'linux'
        else:
            platform_name = 'windows'
        self.socket.sendto(b'files_list:' + platform_name.encode('utf-8'), self.server_address)
        last_packet_time = time.time()
        while time.time() < self.start_time + 5:
            data = None
            try:
                data, addr = self.socket.recvfrom(256)
            except:
                pass
            if data:
                if addr == self.server_address:
                    last_packet_time = time.time()
                    try:
                        file_data = json.loads(data)
                        self.files_list.update(file_data)
                    except:
                        pass
            if last_packet_time < time.time() - 0.5:
                break
        if len(self.files_list) != 0:
            return True
        return False

    def get_files(self):
        for filename in self.files_list:
            if not check_file(filename, self.files_list[filename]['hash']):
                if filename not in protected_files:
                    self.files_to_download.append(filename)
        while time.time() < self.end_time + max_download_time:
            for _thread in self.active_threads.copy():
                if not _thread.is_alive():
                    if _thread.parts_to_get != 0 and _thread.parts_got == _thread.parts_to_get:
                        babase.app.restartRequired = True
                    else:
                        self.files_to_download.append(_thread.filename)
                    self.active_threads.remove(_thread)
            if len(self.active_threads) < 4 and len(self.files_to_download) != 0 and time.time() < self.end_time:
                filename = self.files_to_download[0]
                self.files_to_download.pop(0)
                new_thread = DownloadFileFromServerThread(self.server_address, filename, self.files_list[filename])
                new_thread.start()
                self.active_threads.append(new_thread)
            if len(self.active_threads) == 0 and len(self.files_to_download) == 0:
                break
            if len(self.active_threads) == 0 and time.time() > self.end_time:
                break
            time.sleep(0.1)
        if len(self.active_threads) == 0 and len(self.files_to_download) == 0:
            self.status = 'finished'
            return True
        self.status = 'error'
        return False


class CheckHashThread(threading.Thread):

    def __init__(self, server_name, server_address, our_hash):
        super().__init__(daemon=True)
        self.server_name = server_name
        self.server_address = server_address
        self.server_hash = ''
        self.our_hash = our_hash

    def run(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        self.start_time = time.time()
        self.end_time = self.start_time + 10
        if check_server_ip(self.server_address, self.socket):
            self.get_server_hash()
        self.socket.close()

    def get_server_hash(self):
        import platform
        if platform.system() in ['Linux', 'Android']:
            platform_name = 'linux'
        else:
            platform_name = 'windows'
        while time.time() < self.start_time + 10:
            self.socket.sendto(b'hash:' + platform_name.encode('utf-8'), self.server_address)
            data = None
            try:
                data, addr = self.socket.recvfrom(256)
            except:
                pass
            if data:
                if addr == self.server_address:
                    if data.startswith(b'hash:'):
                        try:
                            self.server_hash = data[5:].decode('utf-8')
                            return True
                        except:
                            pass
        return False

old_connect_to_party = bs.connect_to_party

def new_connect_to_party(address, port, print_progress=False):
    if hasattr(babase.app, 'filesDownloadThread') and babase.app.filesDownloadThread is not None and not babase.app.filesDownloadThread.is_alive():
        babase.app.filesDownloadThread = None
        #babase.app.filesDownloadThreadTimer = None
    server_name = get_server_name(address, port)
    babase.apptimer(0.2, bs.Call(start_check_hash_thread_try, server_name, address, port, 10))
    if server_name is not None:
        hash_data = babase.app.config.get('Saved Media Files')
        if hash_data:
            server_data = hash_data.get(server_name)
            if server_data:
                server_hash = server_data.get('hash')
                if server_hash is not None:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(b'serverhash:' + server_hash.encode('utf-8'), (address, port))
                    sock.close()
                    babase.apptimer(0.1, bs.Call(old_connect_to_party, address, port, print_progress))
                    return
    old_connect_to_party(address, port, print_progress)
    
bs.connect_to_party = new_connect_to_party

def get_server_name(server_address, server_port):
    info = bs.get_connection_to_host_info_2() if hasattr(bs, 'get_connection_to_host_info_2') else bs.get_connection_to_host_info()
    if info is not None and info.name != '':
        return info.name
    saved_servers = babase.app.config.get('Saved Media Files')
    if saved_servers:
        for server_name in saved_servers:
            if saved_servers[server_name]['address'] == server_address and saved_servers[server_name]['port'] == server_port:
                return server_name
    return None

def start_check_hash_thread_try(server_name, address, port, _try):
    new_name = get_server_name(None, None)
    if new_name is not None:
        start_check_hash_thread(new_name, address, port)
        return
    if _try > 0:
        babase.apptimer(0.2, bs.Call(start_check_hash_thread_try, server_name, address, port, _try - 1))
    else:
        start_check_hash_thread('', address, port)

def start_check_hash_thread(server_name, address, port):
    if not hasattr(babase.app, 'filesDownloadThread'):
        babase.app.filesDownloadThread = None
    if babase.app.filesDownloadThread is None:
        our_hash = ''
        if server_name != '':
            hash_data = babase.app.config.get('Saved Media Files')
            if hash_data:
                server_data = hash_data.get(server_name)
                if server_data:
                    our_hash = calculate_overall_hash(server_data.get('files', []))
                    babase.app.config['Saved Media Files'][server_name]['hash'] = our_hash
                    babase.app.config['Saved Media Files'][server_name]['address'] = address
                    babase.app.config['Saved Media Files'][server_name]['port'] = port
                    babase.app.config.commit()
        babase.app.filesDownloadThread = CheckHashThread(server_name, (address, port + 200), our_hash)
        babase.app.filesDownloadThread.start()
        babase.app.filesDownloadThreadTimer = babase.AppTimer(0.02, check_files_thread, repeat=True)

def check_files_thread():
    _thread = babase.app.filesDownloadThread
    if _thread is None or not _thread.is_alive():
        if isinstance(_thread, CheckHashThread):
            #babase.app.filesDownloadThreadTimer = None
            if _thread.server_hash == '':
                babase.app.filesDownloadThread = None
                return
            elif _thread.our_hash == _thread.server_hash:
                babase.app.filesDownloadThread = None
                return
            else:
                hash_data = babase.app.config.get('Saved Media Files')
                if hash_data:
                    for server_name in hash_data:
                        if hash_data[server_name].get('hash', '') == _thread.server_hash:
                            our_hash = calculate_overall_hash(hash_data[server_name].get('files', []))
                            if our_hash == _thread.server_hash:
                                if _thread.server_name != '':
                                    if _thread.server_name not in babase.app.config['Saved Media Files']:
                                        babase.app.config['Saved Media Files'][_thread.server_name] = {}
                                    babase.app.config['Saved Media Files'][_thread.server_name]['address'] = _thread.server_address[0]
                                    babase.app.config['Saved Media Files'][_thread.server_name]['port'] = _thread.server_address[1] - 200
                                    babase.app.config['Saved Media Files'][_thread.server_name]['files'] = hash_data[server_name].get('files', [])
                                    babase.app.config['Saved Media Files'][_thread.server_name]['hash'] = our_hash
                                    babase.app.config.commit()
                                babase.app.filesDownloadThread = None
                                return
                FilesDownloadWindow(_thread.server_name, _thread.server_address, _thread.server_hash)
                babase.app.filesDownloadThread = None
                return
        elif isinstance(_thread, GetFilesThread):
            if not _thread.files_saved:
                _thread.files_saved = True
                files_downloaded = []
                for filename in _thread.files_list:
                    if filename not in _thread.files_to_download:
                        files_downloaded.append(filename)
                if len(files_downloaded) != 0:
                    if _thread.server_name != '':
                        files_downloaded.sort()
                        new_hash = calculate_overall_hash(files_downloaded)
                        if 'Saved Media Files' not in babase.app.config:
                            babase.app.config['Saved Media Files'] = {}
                        saved_servers = babase.app.config.get('Saved Media Files')
                        for server_name in list(saved_servers.keys()):
                            if saved_servers[server_name]['address'] == _thread.server_address[0] and saved_servers[server_name]['port'] == _thread.server_address[1] - 200:
                                saved_servers.pop(server_name)
                        saved_servers[_thread.server_name] = {
                            'address': _thread.server_address[0],
                            'port': _thread.server_address[1] - 200,
                            'hash': new_hash,
                            'files': files_downloaded
                        }
                        babase.app.config.commit()
                    if _thread.status == 'finished':
                        bs.broadcastmessage(
                            'Все файлы скачались', color=(0, 1, 0)
                        )
                    else:
                        bs.broadcastmessage(
                            'Не все файлы скачались', color=(1, 0, 0)
                        )
            if _thread.end_time < time.time() - 30:
                #babase.app.filesDownloadThreadTimer = None
                babase.app.filesDownloadThread = None
    elif isinstance(_thread, GetFilesThread):
        pass
    if hasattr(babase.app, 'downloadStatusWindow') and babase.app.downloadStatusWindow:
        babase.app.downloadStatusWindow._update()

old_party_icon_activate = babase.app.classic.party_icon_activate
def party_icon_activate(origin):
    if (hasattr(babase.app, 'filesDownloadThread')
        and babase.app.filesDownloadThread is not None
        and isinstance(babase.app.filesDownloadThread, GetFilesThread)
    ):
        if (babase.app.filesDownloadThread.is_alive()
            or babase.app.filesDownloadThread.end_time > time.time() - 30
        ):
            if not hasattr(babase.app, 'downloadStatusWindow') or not babase.app.downloadStatusWindow:
                babase.app.downloadStatusWindow = DownloadStatusWindow()
    if hasattr(babase.app, 'restartRequired') and babase.app.restartRequired:
        if not hasattr(babase.app, 'downloadStatusWindow') or not babase.app.downloadStatusWindow:
            babase.app.downloadStatusWindow = DownloadStatusWindow()
    old_party_icon_activate(origin)
babase.app.classic.party_icon_activate = party_icon_activate

class DownloadStatusWindow(bui.Window):
    def __init__(
        self,
        transition: str = 'in_left',
    ):
        uiscale = bui.app.ui_v1.uiscale
        self.length_0 = (365 if uiscale is babase.UIScale.SMALL else
                        480 if uiscale is babase.UIScale.MEDIUM else 540)
        self._width = 0.5 * self.length_0
        self._height = 0.5 * 0.3 * self.length_0
        #pos = (-self.length_0 + 2.3 * self._width - 700, 0.5 * self.length_0 - 1.0 * self._height)
        pos = (-self.length_0 + 2.3 * self._width - 700, 0.5 * self.length_0 - 3.0 * self._height + 160)
        self._base_scale = (
            2.05
            if uiscale is babase.UIScale.SMALL
            else 1.5
            if uiscale is babase.UIScale.MEDIUM
            else 1.2
        )
        self._name = ''
        self._text_color_ = (0, 0, 0)

        top_extra = 15 if uiscale is babase.UIScale.SMALL else 15
        super().__init__(
            root_widget=bui.containerwidget(
                #size=(self._width, self._height + top_extra),
                size=(0, 0),
                transition=transition,
                scale=self._base_scale,
                stack_offset=pos,
                color=(0, 0, 0),
                parent=bui.get_special_widget('overlay_stack'),
                on_outside_click_call=self.close,
            )
        )
        opacity = 0.2
        _thread = babase.app.filesDownloadThread
        if _thread is None:
            opacity = 0.0
        elif not _thread.is_alive():
            if isinstance(_thread, GetFilesThread):
                if _thread.end_time < time.time() - 28:
                    opacity = 0.0
        self.bg = bui.imagewidget(parent=self._root_widget,
            size=(1.2 * self._width, 4.5 * self._height),
            position=(0.1 * self._width, -3.7 * self._height),
            texture=bui.gettexture('softRect2'),
            opacity=opacity,
            color=(1, 1, 1),
        )

        self.bar_x0 = int(0.1 * self.length_0)
        self.bar_x1 = int(0.4 * self.length_0)
        self.text_dx = int(0.15 * self.length_0 - 70)
        self.bar_y0 = int(self._height - 5.0 / 30 * self.length_0)
        self.active_bars = {}
        self.finish_message = None
        self.restart_message = None

    def close(self) -> None:
        """Close the window."""
        # no-op if our underlying widget is dead or on its way out.
        if not self._root_widget or self._root_widget.transitioning_out:
            return
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        babase.app.downloadStatusWindow = None

    def create_status_bar(self, file_download_thread):
        _index = len(self.active_bars)
        min_y = self.bar_y0
        for _bar in list(self.active_bars.values()):
            if _bar['pos'][1] - 2.0 / 30 * self.length_0 < min_y:
                min_y = int(_bar['pos'][1] - 2.0 / 30 * self.length_0)
        x = self.bar_x1 if file_download_thread.start_time >= time.time() - 1.0 else self.bar_x0
        #y = self.bar_y0 - 2.0 / 30 * _index * self.length_0
        y = min_y
        if _index < 8:
            bar_bg = bui.imagewidget(parent=self._root_widget,
                size=(3, 0.3 * self._height + 4),
                position=(x, y),
                texture=bui.gettexture('softRect2'),
                opacity=0.0,
                color=(0.2, 0.8, 1),
            )
            bar_text = bui.textwidget(
                parent=self._root_widget,
                size=(1.12 * self._width, 0.5 * self._height),
                color=(*self._text_color_, 0),
                position=(x + self.text_dx, y),
                text=file_download_thread.filename,
                maxwidth=1.12 * self._width,
                shadow=0.0,
                flatness=0.0,
                v_align='center',
                h_align='left',
                corner_scale=0.7,
                scale=0.0037 * self._width
            )
            self.active_bars[file_download_thread.filename] = {
                'thread': file_download_thread,
                'bg': bar_bg,
                'text': bar_text,
                'index': _index,
                'pos': (x, y),
                'opacity': 0.0,
                #'color': (1, 1, 0),
                'color': (0.2, 0.8, 1),
                'len': 3,
                'k': 0.0
            }

    def _update(self):
        if not self._root_widget:
            babase.app.downloadStatusWindow = None
            return
        if len(self.active_bars) == 0:
            _thread = babase.app.filesDownloadThread
            if hasattr(self, 'message_opacity'):
                self.message_opacity = min(1.0, self.message_opacity + 0.04)
            if _thread is None or not _thread.is_alive():
                if hasattr(babase.app, 'restartRequired') and babase.app.restartRequired:
                    if not hasattr(self, 'message_opacity'):
                        self.message_opacity = 0.0
                    if self.restart_message is None:
                        if _thread is None:
                            h_offset = 0.2 * self._width
                        else:
                            h_offset = -0.1 * self._width
                        self.restart_message = bui.textwidget(
                            parent=self._root_widget,
                            size=(2.24 * self._width, 0.5 * self._height),
                            color=(1, 0.9, 0, 0),
                            position=(-0.1 * self._width, h_offset),
                            text='Перезапустите игру',
                            maxwidth=2.24 * self._width,
                            shadow=0.5,
                            flatness=1.0,
                            v_align='center',
                            h_align='center',
                            corner_scale=0.7,
                            scale=0.003 * self._width
                        )
                    else:
                        bui.textwidget(edit=self.restart_message, color=(1, 0.9, 0, self.message_opacity))
            if _thread is not None and not _thread.is_alive():
                if isinstance(_thread, GetFilesThread):
                    if not hasattr(self, 'message_opacity'):
                        self.message_opacity = 0.0
                    if _thread.end_time < time.time() - 28:
                        if hasattr(babase.app, 'restartRequired') and babase.app.restartRequired:
                            pass
                        else:
                            self.close()
                    elif self.finish_message is None:
                        if _thread.status == 'finished':
                            message_text = 'Все файлы успешно скачались'
                            message_color = (0, 1, 0.2, 0)
                        else:
                            message_text = 'Некоторые файлы не удалось скачать'
                            message_color = (1, 0.0, 0.2, 0)
                        self.finish_message = bui.textwidget(
                            parent=self._root_widget,
                            size=(2.24 * self._width, 0.5 * self._height),
                            color=message_color,
                            position=(-0.1 * self._width, 0),
                            text=message_text,
                            maxwidth=2.24 * self._width,
                            shadow=0.5,
                            flatness=1.0,
                            v_align='center',
                            h_align='center',
                            corner_scale=0.7,
                            scale=0.0037 * self._width
                        )
                    else:
                        if _thread.status == 'finished':
                            bui.textwidget(edit=self.finish_message, color=(0, 1, 0.2, self.message_opacity))
                        else:
                            bui.textwidget(edit=self.finish_message, color=(1, 0, 0.2, self.message_opacity))
                return
        _index = 0
        for filename in list(self.active_bars.keys()):
            _bar = self.active_bars[filename]
            _thread = _bar['thread']
            _error = False
            if _thread.is_alive():
                new_opacity = min(1.0, _bar['opacity'] + 0.036)
                if _thread.parts_to_get != 0:
                    new_k = 1.0 * _thread.parts_got / _thread.parts_to_get
                else:
                    new_k = 0.0
            else:
                new_opacity = max(0.0, _bar['opacity'] - 0.012)
                if _thread.parts_to_get != 0 and _thread.parts_got == _thread.parts_to_get:
                    new_k = 1.0
                else:
                    new_k = _bar['k']
                    _error = True
            if new_k - _bar['k'] > 0.002:
                new_k = _bar['k'] + 0.002 * math.pow((new_k - _bar['k']) / 0.002, 0.3)
            if _error:
                new_color = (1, 0, 0)
                new_len = _bar['len']
            else:
                #new_color = (1 - new_k * 0.9, 1, new_k * 0.1)
                new_color = (0.2 - new_k * 0.2, 0.8 + new_k * 0.2, 1 - new_k * 1.0)
                new_len = max(3, new_k * self._width)
            x, y = _bar['pos']
            if x > self.bar_x0:
                x = max(self.bar_x0, x - 8)
            if y < self.bar_y0 - 2.0 / 30 * _index * self.length_0:
                y = min(self.bar_y0 - 2.0 / 30 * _index * self.length_0, y + 0.04 * self._height)
            bui.imagewidget(edit=self.active_bars[filename]['bg'], size=(new_len, 0.3 * self._height + 4), opacity=0.6 * new_opacity, color=new_color, position=(x, y))
            #bui.textwidget(edit=self.active_bars[filename]['text'], scale=new_opacity * 0.0037 * self._width, position=(x + self.text_dx, y))
            if _thread.is_alive():
                bui.textwidget(edit=self.active_bars[filename]['text'], color=(*self._text_color_, new_opacity), scale=0.0037 * self._width, position=(x + self.text_dx, y))
            else:
                bui.textwidget(edit=self.active_bars[filename]['text'], color=(*self._text_color_, new_opacity), scale=0.0037 * self._width, position=(x + self.text_dx, y))
            _bar['opacity'] = new_opacity
            _bar['color'] = new_color
            _bar['len'] = new_len
            _bar['k'] = new_k
            _bar['pos'] = (x, y)
            if _index < _bar['index']:
                _bar['index'] = _index
            if not _thread.is_alive() and new_opacity < 0.01:
                self.active_bars.pop(filename)
                _bar['bg'].delete()
                _bar['text'].delete()
            _index += 1
        main_thread = babase.app.filesDownloadThread
        if main_thread is not None and main_thread.is_alive():
            for file_thread in main_thread.active_threads:
                if file_thread.is_alive():
                    if file_thread.filename in self.active_bars:
                        pass
                    else:
                        if len(self.active_bars) < 8:
                            self.create_status_bar(file_thread)


class FilesDownloadWindow(bui.Window):
    def __init__(
        self,
        server_name,
        server_address,
        overall_hash,
        transition: str = 'in_left',
    ):
        self._r = 'filesMissingWindow'

        self._bg_color = (0.0, 0.4, 0.8)
        self._bg_color2 = (0.0, 0.5, 1.0)
        uiscale = bui.app.ui_v1.uiscale
        length_0 = (365 if uiscale is babase.UIScale.SMALL else
                        480 if uiscale is babase.UIScale.MEDIUM else 540)
        self._width = 0.7 * length_0
        self._height = 0.7 * 0.4 * length_0
        pos = (-length_0 + 1.75 * self._width - 700, 0.5 * length_0 - 1.0 * self._height)
        self._base_scale = (
            2.05
            if uiscale is babase.UIScale.SMALL
            else 1.5
            if uiscale is babase.UIScale.MEDIUM
            else 1.2
        )
        self._name = ''

        top_extra = 15 if uiscale is babase.UIScale.SMALL else 15
        super().__init__(
            root_widget=bui.containerwidget(
                #size=(self._width, self._height + top_extra),
                size=(0, 0),
                transition=transition,
                scale=self._base_scale,
                stack_offset=pos,
                color=self._bg_color,
                parent=bui.get_special_widget('overlay_stack'),
                on_outside_click_call=self._cancel,
            )
        )
        self._bg_image = bui.imagewidget(parent=self._root_widget,
                                             size=(self._width, self._height + top_extra),
                                             position=(0, 0),
                                             texture=bui.gettexture('softRect2'),
                                             opacity=0.6,
                                             color=(0.0, 0.4, 0.8)
        )
        self._cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(52, 30),
            size=(0, 0),
            scale=0.0,
            autoselect=True,
            label='нет',
            on_activate_call=self._cancel,
            color=self._bg_color2,
            textcolor=(0.9, 0.9, 1.0),
        )
        bui.containerwidget(edit=self._root_widget,
                           cancel_button=self._cancel_button)
        self._download_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(0.3 * self._width, 0.16 * self._height),
            size=(0.5 * self._width, 0.4 * self._height),
            scale=0.8,
            autoselect=False,
            label='да, пожалуйста',
            on_activate_call=self._on_download_press,
            color=self._bg_color2,
            textcolor=(0.9, 0.9, 1.0),
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, 0.67 * self._height),
            size=(0, 0),
            text='Загрузить файлы сервера?',
            color=(0.9, 0.9, 1.0),
            maxwidth=self._width * 0.8,
            scale=1.2,
            h_align='center',
            v_align='center',
        )

        self.server_name = server_name
        self.server_address = server_address
        self.overall_hash = overall_hash

    def _on_download_press(self) -> None:
        bs.broadcastmessage(
            'Скачиваем файлы...', color=(0, 1, 0)
        )
        babase.app.filesDownloadThread = GetFilesThread(self.server_name, self.server_address, self.overall_hash)
        babase.app.filesDownloadThread.start()
        babase.app.filesDownloadThreadTimer = babase.AppTimer(0.02, check_files_thread, repeat=True)
        if not hasattr(babase.app, 'downloadStatusWindow') or not babase.app.downloadStatusWindow:
            babase.app.downloadStatusWindow = DownloadStatusWindow()
        self.close()

    def close(self) -> None:
        """Close the window."""
        # no-op if our underlying widget is dead or on its way out.
        if not self._root_widget or self._root_widget.transitioning_out:
            return
        bui.containerwidget(edit=self._root_widget, transition='out_left')

    def _cancel(self) -> None:
        """Close the window."""
        # no-op if our underlying widget is dead or on its way out.
        if not self._root_widget or self._root_widget.transitioning_out:
            return
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        babase.app.filesDownloadThread = None
        #babase.app.filesDownloadThreadTimer = None


# ba_meta export plugin
class MediaBombaPlugin(babase.Plugin):
    def __init__(self):
        pass
