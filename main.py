""" 
************************************************
Memory-Spiel (Web Edition - Final Style)
************************************************
""" 
import asyncio
import pygame
import random
import os
import sys

# --- KONFIGURATION ---
WINDOW_WIDTH = 450 
WINDOW_HEIGHT = 750 
CARD_SIZE = 64
MARGIN = 5 
GRID_COLS = 6
GRID_ROWS = 7

# Farben
BG_COLOR = (220, 220, 220) 
TEXT_COLOR = (0, 0, 0)
SNAKE_BLUE = (0, 180, 255) # Die Farbe aus dem Snake Spiel

# --- KLASSE KARTE ---
class Karte:
    def __init__(self, bild_pfad, bild_id, grid_x, grid_y):
        self.bild_id = bild_id
        self.grid_x = grid_x
        self.grid_y = grid_y
        
        # Position berechnen
        offset_x = 20
        offset_y = 20
        self.x = offset_x + (grid_x * (CARD_SIZE + MARGIN))
        self.y = offset_y + (grid_y * (CARD_SIZE + MARGIN))
        self.rect = pygame.Rect(self.x, self.y, CARD_SIZE, CARD_SIZE)
        
        self.umgedreht = False
        self.im_spiel = True
        
        self.image_front = None
        self.image_back = None
        self.image_removed = None 
        
        # Bilder laden
        try:
            if os.path.exists(f"assets/{bild_pfad}"):
                img = pygame.image.load(f"assets/{bild_pfad}")
                self.image_front = pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))
            
            if os.path.exists("assets/back.jpeg"):
                img = pygame.image.load("assets/back.jpeg")
                self.image_back = pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))

            if os.path.exists("assets/aufgedeckt.jpeg"):
                img = pygame.image.load("assets/aufgedeckt.jpeg")
                self.image_removed = pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))
        except:
            pass 

    def zeichnen(self, screen):
        if not self.im_spiel:
            if self.image_removed:
                screen.blit(self.image_removed, (self.x, self.y))
            else:
                pygame.draw.rect(screen, (200, 200, 200), self.rect)
            return

        if self.umgedreht:
            if self.image_front:
                screen.blit(self.image_front, (self.x, self.y))
            else:
                pygame.draw.rect(screen, "white", self.rect)
                font = pygame.font.Font(None, 30)
                text = font.render(str(self.bild_id), True, "black")
                screen.blit(text, (self.x + 20, self.y + 20))
        else:
            if self.image_back:
                screen.blit(self.image_back, (self.x, self.y))
            else:
                pygame.draw.rect(screen, "blue", self.rect)
        
        pygame.draw.rect(screen, "black", self.rect, 1)

# --- GLOBALE VARIABLEN ---
karten = []
gemerkte_karten = {} 

# UI Helper
def draw_text(screen, text, x, y, size=30, color="black"):
    font = pygame.font.Font(None, size)
    surf = font.render(str(text), True, color)
    screen.blit(surf, (x, y))

# --- HAUPTFUNKTION ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Memory Web")
    
    # Buttons definieren
    btn_neustart = pygame.Rect(20, 660, 120, 40)
    btn_schummel = pygame.Rect(310, 660, 120, 40)

    global karten, gemerkte_karten
    
    spieler = 0
    punkte_mensch = 0
    punkte_computer = 0
    aufgedeckte = []
    warte_zeit_start = 0
    status = "WARTEN_AUF_ZUG"
    schummel_timer = 0
    schummel_aktiv = False
    computer_step = 0
    computer_wahl = [-1, -1]

    # --- FUNKTION ZUM NEUSTARTEN ---
    def spiel_reset():
        nonlocal spieler, punkte_mensch, punkte_computer, aufgedeckte, status
        nonlocal schummel_aktiv, computer_step, computer_wahl
        
        spieler = 0
        punkte_mensch = 0
        punkte_computer = 0
        aufgedeckte = []
        status = "WARTEN_AUF_ZUG"
        schummel_aktiv = False
        computer_step = 0
        computer_wahl = [-1, -1]
        gemerkte_karten.clear()
        
        bild_namen = [
            "apfel.jpeg", "birne.jpeg", "blume.jpeg", "blume2.jpeg", "ente.jpeg", 
            "fisch.jpeg", "fuchs.jpeg", "igel.jpeg", "kaenguruh.jpeg", "katze.jpeg", 
            "kuh.jpeg", "maus1.jpeg", "maus2.jpeg", "maus3.jpeg", "melone.jpeg", 
            "pilz.jpeg", "ronny.jpeg", "schmetterling.jpeg", "sonne.jpeg", "wolke.jpeg", 
            "maus4.jpeg" 
        ]
        
        temp_liste = []
        for i in range(21):
            name = bild_namen[i] if i < len(bild_namen) else "default.jpeg"
            temp_liste.append((name, i))
            temp_liste.append((name, i))
        random.shuffle(temp_liste)
        
        karten.clear()
        idx = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if idx < len(temp_liste):
                    pfad, bild_id = temp_liste[idx]
                    karten.append(Karte(pfad, bild_id, x, y))
                    idx += 1

    spiel_reset()

    clock = pygame.time.Clock()
    running = True
    
    while running:
        aktuelle_zeit = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # 1. NEUSTART (Immer aktiv)
                if btn_neustart.collidepoint(pos):
                    spiel_reset()
                    continue 

                # 2. Spielzüge
                if status == "WARTEN_AUF_ZUG" and spieler == 0:
                    for i, k in enumerate(karten):
                        if k.rect.collidepoint(pos) and k.im_spiel and not k.umgedreht:
                            k.umgedreht = True
                            aufgedeckte.append(i)
                            gemerkte_karten[i] = k.bild_id 
                            
                            if len(aufgedeckte) == 2:
                                status = "PRUEFEN"
                                warte_zeit_start = aktuelle_zeit
                                
                    if btn_schummel.collidepoint(pos) and not schummel_aktiv:
                        schummel_aktiv = True
                        schummel_timer = aktuelle_zeit
                        status = "SCHUMMELN"
                        for k in karten:
                            if k.im_spiel: k.umgedreht = True

        # --- LOGIK ---
        if status == "PRUEFEN" and aktuelle_zeit - warte_zeit_start > 1200:
            idx1 = aufgedeckte[0]
            idx2 = aufgedeckte[1]
            
            if karten[idx1].bild_id == karten[idx2].bild_id:
                karten[idx1].im_spiel = False
                karten[idx2].im_spiel = False
                if idx1 in gemerkte_karten: del gemerkte_karten[idx1]
                if idx2 in gemerkte_karten: del gemerkte_karten[idx2]
                
                if spieler == 0: punkte_mensch += 1
                else: punkte_computer += 1
            else:
                karten[idx1].umgedreht = False
                karten[idx2].umgedreht = False
                spieler = 1 - spieler 
            
            aufgedeckte = []
            
            if spieler == 1:
                status = "COMPUTER_DENKT"
                computer_step = 1
                warte_zeit_start = aktuelle_zeit
            else:
                status = "WARTEN_AUF_ZUG"

        if status == "COMPUTER_DENKT":
            if computer_step == 1 and aktuelle_zeit - warte_zeit_start > 1000:
                gefunden = False
                w1, w2 = -1, -1
                temp_mem = {}
                for pos, bid in gemerkte_karten.items():
                    if karten[pos].im_spiel:
                        if bid in temp_mem:
                            w1, w2 = temp_mem[bid], pos
                            gefunden = True
                            break
                        temp_mem[bid] = pos
                
                if not gefunden:
                    pool = [i for i, k in enumerate(karten) if k.im_spiel]
                    if len(pool) >= 2:
                        w1 = random.choice(pool)
                        pool.remove(w1)
                        w2 = random.choice(pool)
                
                computer_wahl = [w1, w2]
                if w1 != -1:
                    karten[w1].umgedreht = True
                    aufgedeckte.append(w1)
                computer_step = 2
                warte_zeit_start = aktuelle_zeit
                
            elif computer_step == 2 and aktuelle_zeit - warte_zeit_start > 1000:
                w2 = computer_wahl[1]
                if w2 != -1:
                    karten[w2].umgedreht = True
                    aufgedeckte.append(w2)
                status = "PRUEFEN"
                warte_zeit_start = aktuelle_zeit

        if schummel_aktiv and aktuelle_zeit - schummel_timer > 1500:
            schummel_aktiv = False
            status = "WARTEN_AUF_ZUG"
            for k in karten:
                if k.im_spiel:
                    k.umgedreht = False

        # --- ZEICHNEN ---
        screen.fill(BG_COLOR)
        
        for k in karten:
            k.zeichnen(screen)
            
        ui_y = 530
        draw_text(screen, f"Mensch: {punkte_mensch}", 20, ui_y, 35, "blue" if spieler==0 else "black")
        draw_text(screen, f"PC: {punkte_computer}", 260, ui_y, 35, "red" if spieler==1 else "black")
        
        info = "Du bist dran" if spieler == 0 else "Computer zieht..."
        if punkte_mensch + punkte_computer == 21:
            if punkte_mensch > punkte_computer: info = "GEWONNEN!"
            elif punkte_computer > punkte_mensch: info = "VERLOREN!"
            else: info = "UNENTSCHIEDEN"
            
        draw_text(screen, info, 20, ui_y + 40, 40, "black")
        
        # Button Schummeln (Orange)
        pygame.draw.rect(screen, (255, 165, 0), btn_schummel, border_radius=10) 
        pygame.draw.rect(screen, "black", btn_schummel, 2, border_radius=10)
        text_btn = pygame.font.Font(None, 30).render("Schummeln", True, "black")
        rect_btn = text_btn.get_rect(center=btn_schummel.center)
        screen.blit(text_btn, rect_btn)

        # Button Neustart (SNAKE BLAU)
        pygame.draw.rect(screen, SNAKE_BLUE, btn_neustart, border_radius=10) 
        pygame.draw.rect(screen, "black", btn_neustart, 2, border_radius=10)
        text_neu = pygame.font.Font(None, 30).render("Neustart", True, "black")
        rect_neu = text_neu.get_rect(center=btn_neustart.center)
        screen.blit(text_neu, rect_neu)

        pygame.display.update()
        clock.tick(30)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())