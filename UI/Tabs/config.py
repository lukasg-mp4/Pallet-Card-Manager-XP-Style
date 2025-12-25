from tkinter import font
import tkinter as tk

# Helper to measure text width
def measure_text_width(text):
    f = font.Font(family="Tahoma", size=9, weight="bold")
    return f.measure(f"  {text}  ")

TAB_HEIGHT = 26
TAB_PAD_X = 2
TAB_PAD_Y = 2
UNIFIED_BUFFER = 12 # Extra padding for border/visuals