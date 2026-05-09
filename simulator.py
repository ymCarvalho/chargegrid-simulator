"""
ChargeGrid — Estação de Recarga Elétrica
Versão melhorada com:
  - Seleção visual de potência (22 / 50 / 150 kW)
  - Sliders para bateria inicial e limite alvo
  - arco animado de progresso (canvas)
  - timer em tempo real durante a sessão
  - custo estimado
  - recibo detalhado
  - fluxo em 3 telas: configuração → sessão → recibo
"""

import tkinter as tk
from tkinter import font as tkfont
import datetime
import time
import threading
import math

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────
CAPACIDADE_BATERIA = 75       # kWh

BG          = "#0d1117"
PANEL       = "#161b22"
BORDER      = "#30363d"
GREEN       = "#00d97e"
GREEN_DIM   = "#00995a"
TEXT        = "#e6edf3"
TEXT_DIM    = "#8b949e"
TEXT_DARK   = "#0d1117"
ACCENT_BG   = "#0f2a1e"       # fundo badge "Online"
ACCENT_FG   = "#00d97e"

W, H = 540, 740

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ──────────────────────────────────────────────
# WIDGET: ARC PROGRESS
# ──────────────────────────────────────────────
class ArcProgress(tk.Canvas):
    """Arco que exibe a carga."""

    RADIUS   = 70
    THICK    = 12
    CX = CY  = 90

    def __init__(self, parent, **kwargs):
        size = self.CX * 2
        super().__init__(parent, width=size, height=size,
                         bg=BG, highlightthickness=0, **kwargs)
        self._pct   = 0.0
        self._label = "0"
        self._draw()

    def set_pct(self, pct: float, label: str = None):
        self._pct   = max(0.0, min(100.0, pct))
        self._label = label or f"{pct:.0f}"
        self._draw()

    def _draw(self):
        self.delete("all")
        cx, cy, r, t = self.CX, self.CY, self.RADIUS, self.THICK

        # Trilha de fundo
        self.create_arc(cx-r, cy-r, cx+r, cy+r,
                        start=90, extent=-360,
                        outline=BORDER, width=t, style=tk.ARC)

        # Arco preenchido
        if self._pct > 0:
            extent = -3.6 * self._pct
            color  = lerp_color(GREEN_DIM, GREEN, self._pct / 100)
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=90, extent=extent,
                            outline=color, width=t, style=tk.ARC)

        # texto central
        self.create_text(cx, cy - 6, text=self._label,
                         fill=TEXT, font=("Courier New", 28, "bold"))
        self.create_text(cx, cy + 18, text="%",
                         fill=TEXT_DIM, font=("Courier New", 11))


# ──────────────────────────────────────────────
# WIDGET: CARD SELECIONÁVEL
# ──────────────────────────────────────────────
class SelectCard(tk.Frame):
    def __init__(self, parent, label, sublabel, value, group, callback, **kwargs):
        super().__init__(parent, bg=PANEL, bd=0, highlightthickness=1,
                         highlightbackground=BORDER, **kwargs)
        self.value    = value
        self.group    = group
        self.callback = callback
        self._active  = False

        tk.Label(self, text=label, bg=PANEL, fg=TEXT,
                 font=("DM Sans", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        tk.Label(self, text=sublabel, bg=PANEL, fg=TEXT_DIM,
                 font=("Courier New", 9)).pack(anchor="w", padx=10, pady=(0, 8))

        self.bind("<Button-1>", self._click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._click)

    def _click(self, _=None):
        for card in self.group:
            card.deactivate()
        self.activate()
        self.callback(self.value)

    def activate(self):
        self._active = True
        self.config(highlightbackground=GREEN)

    def deactivate(self):
        self._active = False
        self.config(highlightbackground=BORDER)


# ──────────────────────────────────────────────
# APLICAÇÃO PRINCIPAL
# ──────────────────────────────────────────────
class ChargeGridApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("ChargeGrid — Estação")
        self.configure(bg=BG)
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)

        # Estado
        self.tier     = "comum"
        self.potencia = 22
        self.bat_ini  = tk.IntVar(value=30)
        self.bat_lim  = tk.IntVar(value=85)

        self._build_header()
        self._build_config()
        self._build_session()
        self._build_receipt()

        self._show("config")

    # ──── HEADER ────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20, 0))

        # Logo
        mark = tk.Frame(hdr, bg=GREEN, width=34, height=34)
        mark.pack(side="left")
        mark.pack_propagate(False)
        tk.Label(mark, text="⚡", bg=GREEN, fg="white",
                 font=("Segoe UI", 14)).pack(expand=True)

        tk.Label(hdr, text="CHARGE", bg=BG, fg=TEXT,
                 font=("Courier New", 17, "bold")).pack(side="left", padx=(8, 0))
        tk.Label(hdr, text="GRID", bg=BG, fg=GREEN,
                 font=("Courier New", 17, "bold")).pack(side="left")

        tk.Label(hdr, text=" ● Online ", bg=ACCENT_BG, fg=ACCENT_FG,
                 font=("Courier New", 9)).pack(side="right",
                                               padx=4, pady=4, ipadx=6, ipady=3)

    # ──── TELA CONFIG ────────────────────────────
    def _build_config(self):
        self.frame_config = tk.Frame(self, bg=BG)

        # ── Tipo de usuário ──
        self._section(self.frame_config, "TIPO DE USUÁRIO")

        tier_row = tk.Frame(self.frame_config, bg=BG)
        tier_row.pack(fill="x", padx=24, pady=(0, 16))

        self.tier_cards = []
        cards_data = [
            ("Comum",   "R$ 1,80/kWh + R$ 5 taxa",  "comum"),
            ("Premium", "R$ 1,20/kWh + R$ 2 taxa",  "premium"),
        ]
        for label, sub, val in cards_data:
            c = SelectCard(tier_row, label, sub, val,
                           self.tier_cards, self._set_tier, cursor="hand2")
            c.pack(side="left", expand=True, fill="x", padx=(0, 8), ipady=2)
            self.tier_cards.append(c)
        self.tier_cards[0].activate()

        # ── Potência ──
        self._section(self.frame_config, "POTÊNCIA DO CARREGADOR")

        pow_row = tk.Frame(self.frame_config, bg=BG)
        pow_row.pack(fill="x", padx=24, pady=(0, 16))

        self.pow_cards = []
        powers = [(22, "kW  AC"), (50, "kW  DC"), (150, "kW Ultra")]
        for kw, unit in powers:
            c = SelectCard(pow_row, str(kw), unit, kw,
                           self.pow_cards, self._set_potencia, cursor="hand2")
            c.pack(side="left", expand=True, fill="x", padx=(0, 8), ipady=4)
            self.pow_cards.append(c)
        self.pow_cards[0].activate()

        # ── Sliders ──
        self._section(self.frame_config, "CONFIGURAÇÃO DE CARGA")

        sld_card = tk.Frame(self.frame_config, bg=PANEL, bd=0,
                            highlightthickness=1, highlightbackground=BORDER)
        sld_card.pack(fill="x", padx=24, pady=(0, 20))

        self._slider_row(sld_card, "Bateria atual", self.bat_ini, 5, 70, "%")
        self._slider_row(sld_card, "Limite alvo",   self.bat_lim, 50, 100, "%")

        # ── Botão ──
        self.btn_start = tk.Button(
            self.frame_config,
            text="⚡  INICIAR RECARGA",
            bg=GREEN, fg=TEXT_DARK, activebackground=GREEN_DIM,
            font=("Courier New", 12, "bold"),
            bd=0, cursor="hand2", pady=12,
            command=self._iniciar
        )
        self.btn_start.pack(fill="x", padx=24, pady=(0, 24))

    def _slider_row(self, parent, label, var, from_, to, suffix):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=16, pady=8)

        tk.Label(row, text=label, bg=PANEL, fg=TEXT_DIM,
                 font=("Courier New", 9)).pack(side="left")

        val_lbl = tk.Label(row, text=f"{var.get()}{suffix}", bg=PANEL, fg=GREEN,
                           font=("Courier New", 9, "bold"), width=5)
        val_lbl.pack(side="right")

        def on_change(*_):
            val_lbl.config(text=f"{var.get()}{suffix}")

        tk.Scale(row, variable=var, from_=from_, to=to, orient="horizontal",
                 bg=PANEL, fg=TEXT, troughcolor=BORDER, activebackground=GREEN,
                 highlightthickness=0, bd=0, showvalue=False,
                 command=lambda _: on_change()).pack(side="left", fill="x",
                                                     expand=True, padx=8)

    # ──── TELA SESSÃO ────────────────────────────
    def _build_session(self):
        self.frame_session = tk.Frame(self, bg=BG)

        # Status pill + timer
        top = tk.Frame(self.frame_session, bg=BG)
        top.pack(fill="x", padx=24, pady=(16, 0))

        pill = tk.Frame(top, bg=ACCENT_BG, bd=0,
                        highlightthickness=1, highlightbackground=GREEN)
        pill.pack(side="left")
        self._pill_dot = tk.Label(pill, text="●", bg=ACCENT_BG, fg=GREEN,
                                  font=("Courier New", 9))
        self._pill_dot.pack(side="left", padx=(6, 2), pady=3)
        tk.Label(pill, text="Carregando", bg=ACCENT_BG, fg=ACCENT_FG,
                 font=("Courier New", 9)).pack(side="left", padx=(0, 8), pady=3)

        self.lbl_timer = tk.Label(top, text="00:00", bg=BG, fg=TEXT_DIM,
                                  font=("Courier New", 11))
        self.lbl_timer.pack(side="right")

        # Arco
        self.arc = ArcProgress(self.frame_session)
        self.arc.pack(pady=20)

        # Stats
        stats_row = tk.Frame(self.frame_session, bg=BG)
        stats_row.pack(fill="x", padx=24)

        self.lbl_energy = self._stat_card(stats_row, "Energia",    "0,00", "kWh")
        self.lbl_power  = self._stat_card(stats_row, "Potência",   "—",    "kW")
        self.lbl_cost   = self._stat_card(stats_row, "Custo est.", "R$0",  "")

    def _stat_card(self, parent, label, init_val, unit):
        card = tk.Frame(parent, bg=PANEL, bd=0,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="left", expand=True, fill="x", padx=(0, 8))

        tk.Label(card, text=label, bg=PANEL, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack(pady=(8, 0))
        lbl = tk.Label(card, text=init_val, bg=PANEL, fg=TEXT,
                       font=("Courier New", 14, "bold"))
        lbl.pack()
        tk.Label(card, text=unit, bg=PANEL, fg=TEXT_DIM,
                 font=("Courier New", 8)).pack(pady=(0, 8))
        return lbl

    # ──── TELA RECIBO ────────────────────────────
    def _build_receipt(self):
        self.frame_receipt = tk.Frame(self, bg=BG)

        self._section(self.frame_receipt, "RECIBO DA SESSÃO")

        card = tk.Frame(self.frame_receipt, bg=PANEL, bd=0,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", padx=24)

        self.receipt_inner = card

        # Total
        sep = tk.Frame(self.frame_receipt, bg=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=12)

        total_row = tk.Frame(self.frame_receipt, bg=BG)
        total_row.pack(fill="x", padx=24)

        tk.Label(total_row, text="TOTAL", bg=BG, fg=TEXT_DIM,
                 font=("Courier New", 11, "bold")).pack(side="left")
        self.lbl_total = tk.Label(total_row, text="R$ 0,00", bg=BG, fg=GREEN,
                                  font=("Courier New", 22, "bold"))
        self.lbl_total.pack(side="right")

        # Aprovado
        aprov = tk.Frame(self.frame_receipt, bg=BG)
        aprov.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(aprov, text="✔ Pagamento aprovado", bg=BG, fg=GREEN,
                 font=("Courier New", 10)).pack(side="left")

        # Botão nova sessão
        tk.Button(
            self.frame_receipt,
            text="Nova recarga",
            bg=PANEL, fg=TEXT, activebackground=BG,
            font=("Courier New", 11),
            bd=0, cursor="hand2", pady=10,
            highlightthickness=1, highlightbackground=BORDER,
            command=self._nova_sessao
        ).pack(fill="x", padx=24, pady=20)

    def _receipt_row(self, parent, key, val):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=16, pady=5)
        tk.Label(row, text=key, bg=PANEL, fg=TEXT_DIM,
                 font=("Courier New", 9)).pack(side="left")
        tk.Label(row, text=val, bg=PANEL, fg=TEXT,
                 font=("Courier New", 9, "bold")).pack(side="right")
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=16)

    # ──── NAVEGAÇÃO ──────────────────────────────
    def _show(self, screen: str):
        for f in (self.frame_config, self.frame_session, self.frame_receipt):
            f.pack_forget()

        if screen == "config":
            self.frame_config.pack(fill="both", expand=True, pady=(16, 0))
        elif screen == "session":
            self.frame_session.pack(fill="both", expand=True, pady=(16, 0))
        elif screen == "receipt":
            self.frame_receipt.pack(fill="both", expand=True, pady=(16, 0))

    # ──── LÓGICA ─────────────────────────────────
    def _set_tier(self, t):
        self.tier = t

    def _set_potencia(self, p):
        self.potencia = p

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg=BG, fg=TEXT_DIM,
                 font=("Courier New", 9)).pack(anchor="w", padx=24, pady=(16, 6))

    def _iniciar(self):
        self.btn_start.config(state="disabled")
        self._show("session")

        # Reset UI
        self.arc.set_pct(0, "0")
        self.lbl_energy.config(text="0,00")
        self.lbl_power.config(text=str(self.potencia))
        self.lbl_cost.config(text="R$0")
        self.lbl_timer.config(text="00:00")

        self._start_time = time.time()
        self._run_timer()

        threading.Thread(target=self._simular, daemon=True).start()

    def _run_timer(self):
        elapsed = int(time.time() - self._start_time)
        m = elapsed // 60
        s = elapsed  % 60
        self.lbl_timer.config(text=f"{m:02d}:{s:02d}")
        self._timer_id = self.after(1000, self._run_timer)

    def _simular(self):
        bateria     = float(self.bat_ini.get())
        limite      = float(self.bat_lim.get())
        potencia    = self.potencia
        tarifa      = 1.2 if self.tier == "premium" else 1.8
        taxa        = 2   if self.tier == "premium" else 5
        energia_tot = 0.0
        tempo_min   = 0

        while bateria < limite:
            efic        = 1.0 if bateria < 80 else 0.5
            energia_min = (potencia * efic) / 60
            energia_tot += energia_min
            bateria     += (energia_min / CAPACIDADE_BATERIA) * 100
            bateria      = min(bateria, limite)
            tempo_min   += 1

            prog  = (bateria / limite) * 100
            custo = energia_tot * tarifa + taxa

            self.after(0, lambda p=prog, b=bateria, e=energia_tot, c=custo:
                       self._update_session(p, b, e, c))

            time.sleep(0.06)

        self.after(500, lambda: self._finalizar(
            energia_tot, tarifa, taxa, bateria, tempo_min))

    def _update_session(self, prog, bat, energia, custo):
        self.arc.set_pct(prog, f"{bat:.0f}")
        self.lbl_energy.config(text=f"{energia:.2f}".replace(".", ","))
        self.lbl_cost.config(text=f"R${custo:.0f}")

    def _finalizar(self, energia, tarifa, taxa, bateria, tempo_min):
        if hasattr(self, "_timer_id"):
            self.after_cancel(self._timer_id)

        elapsed  = int(time.time() - self._start_time)
        mm, ss   = elapsed // 60, elapsed % 60
        custo    = energia * tarifa + taxa

        # Limpar recibo anterior
        for w in self.receipt_inner.winfo_children():
            w.destroy()

        rows = [
            ("Tempo de sessão",      f"{mm}min {ss}s"),
            ("Energia transferida",  f"{energia:.2f} kWh".replace(".", ",")),
            ("Bateria final",        f"{bateria:.0f}%"),
            ("Tarifa",               f"R$ {tarifa:.2f}/kWh".replace(".", ",")),
            ("Taxa de sessão",       f"R$ {taxa:.2f}".replace(".", ",")),
            ("Subtotal energia",     f"R$ {energia*tarifa:.2f}".replace(".", ",")),
        ]
        for k, v in rows:
            self._receipt_row(self.receipt_inner, k, v)

        self.lbl_total.config(text=f"R$ {custo:.2f}".replace(".", ","))
        self._show("receipt")

    def _nova_sessao(self):
        self.btn_start.config(state="normal")
        self._show("config")


if __name__ == "__main__":
    app = ChargeGridApp()
    app.mainloop()