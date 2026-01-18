import tkinter as tk
import turtle
import time
import math

# L-SYSTEM ENGINE #
def expand_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_string = ""
        for ch in current:
            next_string += rules.get(ch, ch)
        current = next_string
    return current


# DRAWING ENGINE #
def draw_lsystem(t, instructions, angle, iterations):
    stack = []

    # Auto scale step size
    step = max(2, 20 - iterations * 2)

    turtle.tracer(0, 0)

    total = len(instructions)
    for i, cmd in enumerate(instructions):
        if cmd in ["X", "Y"]:
            continue

        # Gradient color
        ratio = i / total if total else 0
        t.pencolor(ratio, 0.6, 1 - ratio)

        if cmd == "F":
            t.forward(step)
        elif cmd == "+":
            t.right(angle)
        elif cmd == "-":
            t.left(angle)
        elif cmd == "[":
            stack.append((t.position(), t.heading()))
        elif cmd == "]":
            pos, head = stack.pop()
            t.penup()
            t.goto(pos)
            t.setheading(head)
            t.pendown()

    turtle.update()


# PRESETS #
PRESETS = {
    "Custom": ("F", "F:F+F--F+F", 60, 4),
    "Koch Curve": ("F", "F:F+F--F+F", 60, 4),
    "Tree": ("F", "F:F[+F]F[-F]F", 25, 5),
    "Dragon Curve": ("FX", "X:X+YF+,Y:-FX-Y", 90, 10),
}


def apply_preset(choice):
    ax, rules, ang, it = PRESETS[choice]
    axiom_entry.delete(0, tk.END)
    rules_entry.delete(0, tk.END)
    angle_entry.delete(0, tk.END)
    iter_entry.delete(0, tk.END)

    axiom_entry.insert(0, ax)
    rules_entry.insert(0, rules)
    angle_entry.insert(0, ang)
    iter_entry.insert(0, it)


# BUTTON CALLBACK #
def generate():
    start = time.time()

    t.clear()
    t.penup()
    t.goto(0, -250)
    t.setheading(90)
    t.pendown()

    axiom = axiom_entry.get()
    angle = float(angle_entry.get())
    iterations = int(iter_entry.get())

    rules = {}
    for rule in rules_entry.get().split(","):
        k, v = rule.split(":")
        rules[k.strip()] = v.strip()

    final_string = expand_lsystem(axiom, rules, iterations)
    draw_lsystem(t, final_string, angle, iterations)

    end = time.time()
    time_label.config(text=f"Render Time: {end - start:.2f} sec")


# TKINTER WINDOW #
root = tk.Tk()
root.title("L-System Fractal Architect")

canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(side=tk.LEFT)

screen = turtle.TurtleScreen(canvas)
screen.bgcolor("black")

t = turtle.RawTurtle(screen)
t.speed(0)
t.hideturtle()

# CONTROL PANEL #
panel = tk.Frame(root)
panel.pack(side=tk.RIGHT, padx=15)

tk.Label(panel, text="Preset").pack()
preset_var = tk.StringVar(value="Custom")
tk.OptionMenu(panel, preset_var, *PRESETS.keys(), command=apply_preset).pack()

tk.Label(panel, text="Axiom").pack()
axiom_entry = tk.Entry(panel)
axiom_entry.pack()

tk.Label(panel, text="Rules (F:F+F--F+F)").pack()
rules_entry = tk.Entry(panel, width=30)
rules_entry.pack()

tk.Label(panel, text="Angle").pack()
angle_entry = tk.Entry(panel)
angle_entry.pack()

tk.Label(panel, text="Iterations").pack()
iter_entry = tk.Entry(panel)
iter_entry.pack()

tk.Button(panel, text="Generate", command=generate).pack(pady=10)

time_label = tk.Label(panel, text="Render Time: 0.00 sec")
time_label.pack()

# Load default preset
apply_preset("Koch Curve")

root.mainloop()