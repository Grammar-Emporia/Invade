import pygame
import random
import time
import os
from git import Repo
import json
import requests

#obtain highscore from repo

SERVER_URL = "https://website-bq9u.onrender.com"

def getWebserverScores():
    resp = requests.get(f"{SERVER_URL}/score")
    return resp.json()

    
def postScore(player_name, score):
    payload = {'player': player_name, 'score': score}
    resp = requests.post(f"{SERVER_URL}/score", json=payload)

pygame.init()
pygame.font.init()
pygame.mixer.init()

playerName = input("Enter your player name:")

#Highscore
font = pygame.font.SysFont('Comic Sans MS', 30)

#Sounds
pew = pygame.mixer.Sound('pew.mp3')
boom = pygame.mixer.Sound('boom.mp3')
hit = pygame.mixer.Sound('hit.mp3')
powerUpS = pygame.mixer.Sound('powerUp.mp3')

#Images
explosion1 = pygame.image.load("explosion1.png")
explosion2 = pygame.image.load("explosion2.png")
explosion3 = pygame.image.load("explosion3.png")
spaceBG = pygame.image.load("spaceBG.png")
spaceBG = pygame.transform.scale(spaceBG, (1200, 1000))
dead = pygame.image.load("death.png")
dead = pygame.transform.scale(dead, (1200, 1000))
health5 = pygame.image.load("Health5.png")
health5 = pygame.transform.scale(health5, (100, 50))
health4 = pygame.image.load("Health4.png")
health4 = pygame.transform.scale(health4, (100, 50))
health3 = pygame.image.load("Health3.png")
health3 = pygame.transform.scale(health3, (100, 50))
health2 = pygame.image.load("Health2.png")
health2 = pygame.transform.scale(health2, (100, 50))
health1 = pygame.image.load("Health1.png")
health1 = pygame.transform.scale(health1, (100, 50))
coin = pygame.image.load("coin1.png")
coin = pygame.transform.scale(coin, (100, 50))
barr = pygame.image.load("barr.png")
barr = pygame.transform.scale(barr, (10, 300))



# screen
screenW = 1200
screenH = 1000
screen = pygame.display.set_mode((screenW, screenH))
pygame.display.set_caption('Invader')

def restartScreen(score, scoreboardList):

    restartRunning = True

    titleFont = pygame.font.SysFont('Comic Sans MS', 60)
    scoreFont = pygame.font.SysFont('Comic Sans MS', 40)
    instructionFont = pygame.font.SysFont('Comic Sans MS', 30)

    scoreboardSorted = sorted(scoreboardList, key=lambda x: x['score'], reverse=True)

    nameScore = [f"{entry['player']}: {entry['score']}" for entry in scoreboardSorted]

    while restartRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    restartRunning = False

        screen.fill((0, 0, 0))

        gameOverText = titleFont.render("GAME OVER", True, (255, 0, 0))
        screen.blit(gameOverText, (screenW // 2 - gameOverText.get_width() // 2, screenH // 8))

        yourScore = scoreFont.render(f"Your Score: {score}", True, (255, 255, 255))
        screen.blit(yourScore, (screenW // 2 - yourScore.get_width() // 2, screenH // 5))

        highScoresTitle = scoreFont.render("High Scores", True, (255, 255, 0))
        screen.blit(highScoresTitle, (screenW // 2 - highScoresTitle.get_width() // 2, screenH // 3))

        for i, scoreEntry in enumerate(nameScore[:5]):
            scoreText = scoreFont.render(scoreEntry, True, (255, 255, 255))
            screen.blit(
                scoreText,
                (screenW // 2 - scoreText.get_width() // 2, screenH // 3 + 50 + i * 40)
            )

        restartText = instructionFont.render("Press ENTER to restart", True, (0, 255, 0))
        screen.blit(restartText, (screenW // 2 - restartText.get_width() // 2, screenH // 1.5))

        pygame.display.flip()
        pygame.time.delay(100)


def startScreen():
    restartRunning = True
    titleFont = pygame.font.SysFont('Comic Sans MS', 60) 
    optionFont = pygame.font.SysFont('Comic Sans MS', 40)  
    while restartRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  
                    restartRunning = False
                    return "easy"
                if event.key == pygame.K_2:  
                    restartRunning = False
                    return "normal"
                if event.key == pygame.K_3:  
                    restartRunning = False
                    return "hard"
        

        screen.fill((0, 0, 0))  #bg
        
        
        titleText = titleFont.render("ARCADE INVADERS", True, (255, 255, 0))
        screen.blit(titleText, (screenW // 2 - titleText.get_width() // 2, screenH // 6))
        
      
        restartText = optionFont.render("Select Your Difficulty", True, (255, 0, 0))
        screen.blit(restartText, (screenW // 2 - restartText.get_width() // 2, screenH // 3))
        
        
        easyText = optionFont.render("1. EASY", True, (0, 255, 0))
        normalText = optionFont.render("2. NORMAL", True, (255, 255, 0))
        hardText = optionFont.render("3. HARD", True, (255, 0, 0))
        
        screen.blit(easyText, (screenW // 2 - easyText.get_width() // 2, screenH // 2))
        screen.blit(normalText, (screenW // 2 - normalText.get_width() // 2, screenH // 2 + 50))
        screen.blit(hardText, (screenW // 2 - hardText.get_width() // 2, screenH // 2 + 100))
        
    
        pygame.display.flip()
        pygame.time.delay(100)


#Ship movement limit
def limit(imgW, imgH, X, Y):
    global screenW, screenH
    if X > screenW - imgW:
        X = screenW - imgW
    if X < 0:
        X = 0
    if Y > screenH - imgH:
        Y = screenH - imgH
    if Y < 0:
        Y = 0
    return X, Y

#Alien automated movements
def alienMovement(imgW, imgH, X, Y, direction, speed):
    X += speed * direction

    if X > screenW - imgW or X < 0:
        Y += 25
        direction *= -1 # reverse direction if hit a wall

    return X, Y, direction

#Spawn single random alien
def spawnRanAlien():
    ranNum = random.randint(0, 400)
    ranNum1 = random.randint(0, 400)
    ranNum2 = random.randint(1, 3)
    if ranNum2 == 1:
        alien = Alien1(ranNum, ranNum1)
    elif ranNum2 ==2:
        alien = Alien2(ranNum, ranNum1) 
    else:
        alien = Alien2(ranNum, ranNum1)
    aliens.add(alien)
    allSprites.add(alien)    
    

#formation of single hit aliens
def alienFormation(amount):
    x = 0
    i = 0
    while i != amount:
        ranalien = random.randint(1,2)
        ranY = random.randint(100,300)
        if ranalien == 1:
            alien = Alien1(x, ranY)
            allSprites.add(alien)
            aliens.add(alien)
        else:
            alien = Alien2(x, ranY)
            allSprites.add(alien)
            aliens.add(alien)
        x = x + 200
        if x > screenW - 50:  
            x = 0
        i = i+1
        
#formation of multi-hit aliens
def alienFormation2(amount):
    x = 0
    i = 0
    while i != amount:
        ranNumm = random.randint(1,3)
        ranY = random.randint(100,300)
        if ranNumm == 1:
            alien = Alien3(x, ranY)
        elif ranNumm ==2:
            alien = Alien4(x, ranY)
        else:
            alien = Alien5(x, ranY)
        allSprites.add(alien)
        aliens.add(alien)
        x = x + 200
        if x > screenW - 50:  
            x = 0
        i = i+1
        
        

class AlienBase(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.direction = 1
        self.spawnTime = pygame.time.get_ticks()
        self.hit_count = 0
        self.speed = 8
        explosion1 = pygame.image.load("explosion1.png")
        explosion1 = pygame.transform.scale(explosion1, (50, 45))
        explosion2 = pygame.image.load("explosion2.png")
        explosion2 = pygame.transform.scale(explosion2, (50, 45))
        explosion3 = pygame.image.load("explosion3.png")
        explosion3 = pygame.transform.scale(explosion3, (50, 45))
        self.exploding = False
        self.explodingTime = 0
        self.explodingFrames = [
            explosion1,
            explosion2,
            explosion3
        ]

    def update(self):
        selfW = self.image.get_width()
        selfH = self.image.get_height()
        currentTime = pygame.time.get_ticks()
        if self.exploding:
            if currentTime - self.explodingTime > 200:
                self.explodingTime = currentTime
                self.image = self.explodingFrames.pop(0)
                if not self.explodingFrames:
                    self.kill()
        else:
            self.rect.x, self.rect.y, self.direction = alienMovement(selfW, selfH, self.rect.x, self.rect.y, self.direction, self.speed)

    def take_hit(self):
        global lvl
        self.hit_count += 1
        self.exploding = True



class Alien1(AlienBase):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = pygame.image.load("alien1.png")
        self.image = pygame.transform.scale(self.image, (50, 45))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Alien2(AlienBase):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = pygame.image.load("alien2.png")
        self.image = pygame.transform.scale(self.image, (50, 45))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 15

class Alien4(AlienBase):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = pygame.image.load("alien2.png")
        self.image = pygame.transform.scale(self.image, (50, 45))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 15
        self.lastTeleport = pygame.time.get_ticks()

    def update(self):
        currentTime = pygame.time.get_ticks()
        if self.exploding:
            if currentTime - self.explodingTime > 200:
                self.explodingTime = currentTime
                self.image = self.explodingFrames.pop(0)
                if not self.explodingFrames:
                    self.kill()

        randomNumber1 = random.randint(200,1000)
        randomNumber2 = random.randint(200,1000)
        if currentTime - self.lastTeleport >= 1000:
            self.rect.x = randomNumber1
            self.rect.x = randomNumber2
            self.lastTeleport = currentTime


class Boss(AlienBase):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = pygame.image.load("boss.png")
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def take_hit(self):
        global lvl
        self.hit_count += 1
        if self.hit_count > 8 * lvl:
            self.exploding = True
        

class Alien3(AlienBase):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = pygame.image.load("alien3.png")
        self.image = pygame.transform.scale(self.image, (50, 45))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 20

    def take_hit(self):
        self.hit_count += 1
        if self.hit_count == 1:
            self.image = pygame.image.load("alien3OneHit.png")  # Replace with the one-hit image
            self.image = pygame.transform.scale(self.image, (50, 45))
        elif self.hit_count == 2:
            self.image = pygame.image.load("alien3TwoHit.png")  # Replace with the two-hit image
            self.image = pygame.transform.scale(self.image, (50, 45))
        elif self.hit_count >= 3:
            self.exploding = True  # Alien dies after 3 hits

class PlayerShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        #image changes
        self.image = pygame.image.load("ship.png")
        self.image = pygame.transform.scale(self.image, (75, 75))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, barriers):
        selfW = self.image.get_width()
        selfH = self.image.get_height()
        keys = pygame.key.get_pressed()

        old_x, old_y = self.rect.x, self.rect.y

        if keys[pygame.K_w]:
            self.rect.y -= 10
        if keys[pygame.K_a]:
            self.rect.x -= 10
        if keys[pygame.K_s]:
            self.rect.y += 10
        if keys[pygame.K_d]:
            self.rect.x += 10

        if pygame.sprite.spritecollide(self, barriers, False):
            self.rect.x, self.rect.y = old_x, old_y
            
        self.rect.x, self.rect.y = limit(selfW, selfH, self.rect.x, self.rect.y)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        #image changes
        self.image = pygame.image.load("laser.png")
        self.image = pygame.transform.scale(self.image, (5, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.rect.y -= 30
        if self.rect.bottom < 0: #goes off screen
            self.kill()
        
        
class alienLaser(Laser):
    def __init__(self, x, y):
        super().__init__(x, y)
        #image changes
        self.image = pygame.image.load("alienLaser.png")
        self.image = pygame.transform.scale(self.image, (10, 25))

    def update(self):
        self.rect.y += 10
        if self.rect.top > screenH:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        #image changes
        self.image = pygame.image.load("coin1.png")
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Alien5(AlienBase):
    def __init__(self, x, y, split=False, direction=1):
        super().__init__(x, y)
        self.image = pygame.image.load("alien5.png")
        size = (30, 30) if split else (50, 45) 
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 8
        self.hit_count = 0
        self.split = split  
        self.direction = direction  

    def update(self):
        selfW = self.image.get_width()
        selfH = self.image.get_height()
        currentTime = pygame.time.get_ticks()

        if self.exploding:
            if currentTime - self.explodingTime > 200:
                self.explodingTime = currentTime
                if self.explodingFrames:
                    self.image = self.explodingFrames.pop(0)
                else:
                    self.kill()
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.x < 0 or self.rect.x > screenW - selfW:
                self.direction *= -1  

    def take_hit(self):
        self.hit_count += 1
        if self.hit_count == 1 and not self.split:
            alien1 = Alien5(self.rect.x - 30, self.rect.y, split=True, direction=-1)
            alien2 = Alien5(self.rect.x + 30, self.rect.y, split=True, direction=1)
            
            aliens.add(alien1, alien2)
            allSprites.add(alien1, alien2)
            
            self.kill()  
        elif self.hit_count >= 1 and self.split:
            self.exploding = True
            self.explodingTime = pygame.time.get_ticks()
        

class Barr(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("barr.png")
        self.image = pygame.transform.scale(self.image, (200, 30)) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1  
        

#start screen
hardness = startScreen()

if hardness == "easy":
    playerLives = 5
    bossWaitTime = 600
    waitPlayerTime = 100
    ogPlayerTime = 100
    alienShotWait1 = 1000
    alienShotWait2 = 2500
    alienAmount = 2
elif hardness == "normal":
    playerLives = 5
    bossWaitTime = 500
    waitPlayerTime = 200
    alienShotWait1 = 800
    alienShotWait2 = 2000
    ogPlayerTime = 200
    alienAmount = 2
elif hardness == "hard":
    playerLives = 3
    bossWaitTime = 250
    waitPlayerTime = 200
    ogPlayerTime = 200
    alienShotWait1 = 500
    alienShotWait2 = 1000
    alienAmount = 3


lvl = 1
ranNum = random.randint(0, 400)
# sprite groups
player = PlayerShip(500, 700)  
alien = Alien1(ranNum, ranNum)


randomCoordx = random.randint(100,1000)
randomCoordy = random.randint(100,1000)
coin = Coin(randomCoordx,randomCoordy) 

lasers = pygame.sprite.Group()
aliens = pygame.sprite.Group()
aliens3 = pygame.sprite.Group()
allSprites = pygame.sprite.Group()
alienLasers = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()
coinGroup = pygame.sprite.Group()
barrGroup = pygame.sprite.Group()


playerGroup.add(player)
allSprites.add(player)  
allSprites.add(alien)
aliens.add(alien)
aliens3.add(alien)
coinGroup.add(coin)

deadState = False
lastShotTime = 0 #placeholder
playerDamage = 0
lastAlienShotTime = 0
amount = 1
score = 0     
# main loop
running = True
notAlreadyPlayed = True
lvlNotAlreadyPlayed = True
soundNotAlreadyPlayed = True
notSpawnedBoss = True
bossShotTime = 0
powerUp = False
lastPowerUp = 10000
coinStages = []
powerUpStage = 3
powerUpLvl = []
spawnStage = random.randint(2,5)
powerUpLaser = False
superPowerUpLaser = False
num = random.randint(1,2)
score = int(score)
barrIsDead = False

scoreboard = getWebserverScores()
scoreboardSorted = sorted(scoreboard, key=lambda x: x['score'], reverse=True)
if scoreboardSorted:
    currentScore = scoreboardSorted[0]['score']
else:
    currentScore = 0

while running:

    if not barrIsDead and not any(isinstance(sprite, Barr) for sprite in allSprites):
        barr = Barr(x=screenW // 2 - 550, y=screenH - 300)
        allSprites.add(barr)
        barrGroup.add(barr)

    if deadState:
        #change highscore
        biggerThan = []
        score = int(score)
        postScore(playerName, score)

        scoreboard = getWebserverScores()

        restartScreen(score, scoreboard)

        scoreboardSorted = sorted(scoreboard, key=lambda x: x['score'], reverse=True)
        if scoreboardSorted:
            currentScore = scoreboardSorted[0]['score']
        else:
            currentScore = 0
        
        restartScreen(score, currentScore, names)

        for alien in aliens:
            alien.kill()
        #reset game
        score = 0
        lvl = 1
        playerLives = 5
        player = PlayerShip(500, 700)
        playerGroup.add(player)
        allSprites.add(player)
        lastPowerUp = 10000
        powerUpLvl = []
        coinStages = []
        deadState = False

    if lvl % 11 == 0 and notSpawnedBoss:
        alien = Boss(200, 200)
        allSprites.add(alien)
        aliens.add(alien)
        notSpawnedBoss = False
    
    if lvl % 11 != 0:
        notSpawnedBoss = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if lvl % 10 != 0:
        notAlreadyPlayed = True

    if lvl % 5 != 0:
        lvlNotAlreadyPlayed = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        if pygame.time.get_ticks() - lastShotTime > waitPlayerTime:
            laser = Laser(player.rect.centerx, player.rect.top) #adds laser to ships coords, idk why its called centerx and top...
            lasers.add(laser)
            allSprites.add(laser)
            if powerUpLaser:
                if soundNotAlreadyPlayed:
                    soundNotAlreadyPlayed = False
                laser = Laser(player.rect.centerx + 25, player.rect.top) 
                lasers.add(laser)
                allSprites.add(laser)
                laser = Laser(player.rect.centerx - 25, player.rect.top)
                lasers.add(laser)
                allSprites.add(laser)
            if superPowerUpLaser:
                laser = Laser(player.rect.centerx + 25, player.rect.top) 
                lasers.add(laser)
                allSprites.add(laser)
                laser = Laser(player.rect.centerx + 70, player.rect.top) 
                lasers.add(laser)
                allSprites.add(laser)
                laser = Laser(player.rect.centerx - 25, player.rect.top)
                lasers.add(laser)
                allSprites.add(laser)
                laser = Laser(player.rect.centerx - 70, player.rect.top)
                lasers.add(laser)
                allSprites.add(laser)
            pygame.mixer.Sound.play(pew)
            lastShotTime = pygame.time.get_ticks() #adds last shot to list
    
    for laser in lasers:
        collidedAliens = pygame.sprite.spritecollide(laser, aliens, False)  # Check for collisions with Alien1, Alien2, etc.
        if collidedAliens:
            laser.kill()  # Remove the laser
        for alien in collidedAliens:
            if not alien.exploding:
                alien.take_hit()  #alien takes damage
                pygame.mixer.Sound.play(boom)
                score += 1

    if len(aliens) == 0: #checks if all aliens have been killed
        for laser in lasers:
            laser.kill()
        amount = alienAmount + lvl
        ranNum = random.randint(1,2)
        if ranNum == 1:
            alienFormation(amount)
        else:
            alienFormation2(amount)
        lvl = lvl + 1
       



    for laser in alienLasers:  
        collidedPlayer = pygame.sprite.spritecollide(laser, playerGroup, False) #Unlike i thought 'Flase' in this case doesnt mean not colliding, it js doesnt auto remove it
            #collidedAliens returns a list of the lasers and aliens that have collidedAliens
        if collidedPlayer:
            laser.kill()  
            playerLives = playerLives - 1
            pygame.mixer.Sound.play(hit) 
            playerDamage = pygame.time.get_ticks()
            if playerLives == 0:
                player.kill()
                deadState = True
                
    for alien in aliens: #all aliens
            collidedAlien = pygame.sprite.spritecollide(player, aliens, False) #Unlike i thought 'Flase' in this case doesnt mean not colliding, it js doesnt auto remove it
            #collidedAliens returns a list of the lasers and aliens that have collidedAliens
            if collidedAlien:  
                player.rect.y += 100
                playerLives = playerLives - 1
                pygame.mixer.Sound.play(hit)
                playerDamage = pygame.time.get_ticks()
                if playerLives == 0:
                    player.kill()
                    deadState = True

    for laser in alienLasers:
        if pygame.sprite.collide_rect(laser, barr):
            laser.kill()   

    for laser in lasers:
        if pygame.sprite.collide_rect(laser, barr):
            laser.kill()  

    for alien in aliens:
        if pygame.sprite.collide_rect(alien, barr):
            barr.kill() 
            barrIsDead = True
            alien.exploding = True  


    if pygame.time.get_ticks() - playerDamage < 150:
        player.image = pygame.image.load("ship2.png")
        player.image = pygame.transform.scale(player.image, (75, 75))
    else:
        player.image = pygame.image.load("ship.png")
        player.image = pygame.transform.scale(player.image, (75, 75))
  
    for alien in aliens:
        if alien.rect.y > screenH:
            player.kill()
            deadState = True
    
    for alien in aliens3:
        if alien.rect.y > screenH:
            player.kill()
            deadState = True
                
            
    for alien in aliens:
        if isinstance(alien, Boss): #checks if its a boss
            #boss shoots
            if pygame.time.get_ticks() - bossShotTime > bossWaitTime:  
                aLaser = alienLaser(alien.rect.centerx, alien.rect.bottom)  #adds laser to boss
                alienLasers.add(aLaser)
                allSprites.add(aLaser)
                bossShotTime = pygame.time.get_ticks()  #update last shot time
        else:
            #non-boss logic
            if pygame.time.get_ticks() - lastAlienShotTime > ranNum:  
                ranNum = random.randint(alienShotWait1, alienShotWait2)  #shooting interval
                if pygame.time.get_ticks() - alien.spawnTime > ranNum:  
                    aLaser = alienLaser(alien.rect.centerx, alien.rect.bottom)  
                    alienLasers.add(aLaser)
                    allSprites.add(aLaser)
                lastAlienShotTime = pygame.time.get_ticks()

    playerGroup.update(barrGroup)
    for sprite in allSprites:
        if sprite != player:
            sprite.update()


    screen.blit(spaceBG, (0, 0))
    
    
    
    if lvl == spawnStage and lvl not in coinStages:
        coinGroup.add(coin)
        allSprites.add(coin)
        coinStages.append(lvl)
        spawnStage += random.randint(2,11)
        
    #coin powerup logic
    for coin in coinGroup:  
        collidedCoin = pygame.sprite.spritecollide(coin, playerGroup, False) 
        if collidedCoin:
            coin.kill()
            pygame.mixer.Sound.play(powerUpS)
            powerUpLvl.append(lvl)
            num = random.randint(1,2)
            healthApplied = False
            
    #once boss is beat
    if lvl >= 12:
        powerUpLaser = True
        waitPlayerTime -= 1 + lvl

    #apply powerup
    if lvl in powerUpLvl:
        if num == 1:
            if lvl >= 12:
                superPowerUpLaser = True
            waitPlayerTime = 50
            powerUpLaser = True
        if num == 2 and healthApplied == False:
            playerLives = playerLives + 1
            notAlreadyPlayed = False
            healthApplied = True
    else: 
        waitPlayerTime = ogPlayerTime
        powerUpLaser = False
        superPowerUpLaser = False
        notAlreadyPlayed = True

    if playerLives > 5:
        playerLives = 5
    if playerLives == 5:
        screen.blit(health5, (0, 0))
    if playerLives == 4:
        screen.blit(health4, (0, 0))
    if playerLives == 3:
        screen.blit(health3, (0, 0))
    if playerLives == 2:
        screen.blit(health2, (0, 0))
    if playerLives == 1:
        screen.blit(health1, (0, 0))

    allSprites.draw(screen)
    score = str(score)
    lvl = str(lvl)

    scoreTxt = font.render(f"Score: {score}", False, (0, 255, 0))
    scoreRect = scoreTxt.get_rect()
    highScoreTxt = font.render(f"High Score: {currentScore}", False, (0, 255, 0))
    lvlTxt = font.render(f"Level: {lvl}", False, (0, 255, 0))
    lvlRect = lvlTxt.get_rect()

    screen.blit(scoreTxt, (screenW - scoreRect.width, 0))
    screen.blit(lvlTxt, (0, 50))
    screen.blit(highScoreTxt, (1200 // 2.25, 0))
    
   

    pygame.display.flip()
    score = int(score)
    lvl = int(lvl)

   
pygame.quit()
