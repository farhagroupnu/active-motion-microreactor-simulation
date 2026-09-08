#!/usr/bin/env python3
"""
Active Brownian predator-prey simulation.

This script simulates Brownian prey and active Brownian predators under
three predator-speed protocols:
    1. Constant speed
    2. Exponential speed decay
    3. Segmented exponential decay (oscillatory/refueling-like)

Outputs:
    simulation.mp4
    predator_trajectories.png
    prey_count.png
    predator_trajectories.csv
    predator_trajectories_wide.csv
    prey_count.csv
    predator_speed.csv
    predator_msd.csv

The simulation is deterministic when RANDOM_SEED is unchanged.
"""

import csv
import math
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# Parameters
# ============================================================

WIDTH, HEIGHT = 1000, 1000
TEXT_AREA_HEIGHT = 40

N_PREY = 20_000
N_PRED = 125
PREY_SPEED = 250

# Active Brownian motion parameters for predators
ACTIVE_DIFFUSION = 0.1
ROTATIONAL_DIFFUSION = 0.1
DT = 1.0

# Predator speed mode
# 1 = constant
# 2 = exponential decay
# 3 = segmented exponential decay
PRED_SPEED_MODE = 1

PRED_SPEED_INIT = 1.0
PRED_SPEED_FINAL = 0.001
PRED_SPEED_SEGMENTS = 5
EPSILON = 0.0001

STEPS = 5000
FRAME_INTERVAL = 20
VIDEO_FPS = 25
RANDOM_SEED = 42

# Global decay rate for modes 2 and 3.
DECAY_RATE = (
    -math.log(EPSILON / (PRED_SPEED_INIT - PRED_SPEED_FINAL)) / STEPS
)

# Output directory
OUTPUT_DIR = Path("results")

OUTPUT_VIDEO = OUTPUT_DIR / "simulation.mp4"
OUTPUT_TRAJECTORY_PNG = OUTPUT_DIR / "predator_trajectories.png"
OUTPUT_COUNT_PNG = OUTPUT_DIR / "prey_count.png"
OUTPUT_TRAJECTORY_CSV = OUTPUT_DIR / "predator_trajectories.csv"
OUTPUT_TRAJECTORY_WIDE_CSV = OUTPUT_DIR / "predator_trajectories_wide.csv"
OUTPUT_COUNT_CSV = OUTPUT_DIR / "prey_count.csv"
OUTPUT_SPEED_CSV = OUTPUT_DIR / "predator_speed.csv"
OUTPUT_MSD_CSV = OUTPUT_DIR / "predator_msd.csv"

# Colors (RGB, used by PIL)
COLOR_PREY = (170, 121, 58)
COLOR_PRED = (255, 99, 71)

PREY_RADIUS = 2
PRED_RADIUS = 8
PREDATION_RADIUS = 1.0


# ============================================================
# Initialization
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
np.random.seed(RANDOM_SEED)

prey_pos = np.random.rand(N_PREY, 2) * [WIDTH, HEIGHT]
pred_pos = np.random.rand(N_PRED, 2) * [WIDTH, HEIGHT]
pred_angles = np.random.uniform(0, 2 * np.pi, N_PRED)

pred_trajectories = [[] for _ in range(N_PRED)]
for i in range(N_PRED):
    pred_trajectories[i].append(pred_pos[i].copy())

prey_count = [N_PREY]
pred_speed_history = []


# ============================================================
# Helper functions
# ============================================================

def apply_boundary(positions):
    """Reset out-of-bounds particles to random locations in the canvas."""
    out = (
        (positions[:, 0] < 0)
        | (positions[:, 0] >= WIDTH)
        | (positions[:, 1] < 0)
        | (positions[:, 1] >= HEIGHT)
    )
    n_out = np.sum(out)
    if n_out > 0:
        positions[out] = np.random.rand(n_out, 2) * [WIDTH, HEIGHT]


def move_prey(positions, speed):
    """Move prey by a fixed step in a random direction."""
    angles = np.random.rand(len(positions)) * 2 * np.pi
    positions[:, 0] += speed * np.cos(angles)
    positions[:, 1] += speed * np.sin(angles)


def active_move_pred(
    positions, angles, speed, active_diff, rot_diff, dt=1.0
):
    """
    Active Brownian motion for predators.

    The orientation changes by rotational diffusion. The displacement
    contains a persistent active component plus translational diffusion.
    """
    angles += np.sqrt(2 * rot_diff * dt) * np.random.randn(len(angles))

    dx = (
        speed * np.cos(angles) * dt
        + np.sqrt(2 * active_diff * dt) * np.random.randn(len(angles))
    )
    dy = (
        speed * np.sin(angles) * dt
        + np.sqrt(2 * active_diff * dt) * np.random.randn(len(angles))
    )

    positions[:, 0] += dx
    positions[:, 1] += dy

    return positions, angles


def predation(pred_positions, prey_positions, radius=PREDATION_RADIUS):
    """Remove prey within the predation radius of any predator."""
    if len(prey_positions) == 0:
        return prey_positions

    diff = (
        pred_positions[:, np.newaxis, :]
        - prey_positions[np.newaxis, :, :]
    )
    dist = np.sqrt(np.sum(diff**2, axis=-1))

    prey_indices = np.unique(np.where(dist <= radius)[1])
    if len(prey_indices) == 0:
        return prey_positions

    mask = np.ones(len(prey_positions), dtype=bool)
    mask[prey_indices] = False
    return prey_positions[mask]


def get_predator_speed(step):
    """Return predator speed for the selected speed protocol."""
    if PRED_SPEED_MODE == 1:
        return PRED_SPEED_INIT

    if PRED_SPEED_MODE == 2:
        return PRED_SPEED_FINAL + (
            PRED_SPEED_INIT - PRED_SPEED_FINAL
        ) * np.exp(-DECAY_RATE * step)

    if PRED_SPEED_MODE == 3:
        seg_len = STEPS / PRED_SPEED_SEGMENTS
        seg_index = int(step // seg_len)
        seg_index = min(seg_index, PRED_SPEED_SEGMENTS - 1)

        relative_step = step - seg_index * seg_len

        # Each segment restarts from the initial speed.
        return PRED_SPEED_FINAL + (
            PRED_SPEED_INIT - PRED_SPEED_FINAL
        ) * np.exp(-DECAY_RATE * relative_step)

    raise ValueError("PRED_SPEED_MODE must be 1, 2, or 3")


def get_arial_font(size=24):
    """Try Arial; fall back to a common PIL font if unavailable."""
    candidates = [
        "Arial.ttf",
        "arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
    ]

    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            pass

    print("Warning: Arial font not found; using PIL default font.")
    return ImageFont.load_default()


def render_frame(
    prey_positions,
    predator_positions,
    step,
    predator_speed,
    current_prey_count,
):
    """Render one simulation frame with a bottom information strip."""
    img_sim = Image.new(
        "RGB", (WIDTH, HEIGHT), color=(255, 255, 255)
    )
    draw_sim = ImageDraw.Draw(img_sim)

    # Prey
    for x, y in prey_positions:
        ix = int(round(x))
        iy = int(round(HEIGHT - 1 - y))
        ix = np.clip(ix, 0, WIDTH - 1)
        iy = np.clip(iy, 0, HEIGHT - 1)

        draw_sim.ellipse(
            (
                ix - PREY_RADIUS,
                iy - PREY_RADIUS,
                ix + PREY_RADIUS,
                iy + PREY_RADIUS,
            ),
            fill=COLOR_PREY,
        )

    # Predators
    for x, y in predator_positions:
        ix = int(round(x))
        iy = int(round(HEIGHT - 1 - y))
        ix = np.clip(ix, 0, WIDTH - 1)
        iy = np.clip(iy, 0, HEIGHT - 1)

        draw_sim.ellipse(
            (
                ix - PRED_RADIUS,
                iy - PRED_RADIUS,
                ix + PRED_RADIUS,
                iy + PRED_RADIUS,
            ),
            fill=COLOR_PRED,
        )

    new_img = Image.new(
        "RGB",
        (WIDTH, HEIGHT + TEXT_AREA_HEIGHT),
        color=(255, 255, 255),
    )
    new_img.paste(img_sim, (0, 0))

    draw = ImageDraw.Draw(new_img)
    font = get_arial_font(size=24)

    mode_text = {
        1: "Constant",
        2: "Exp Decay",
        3: (
            f"Segmented (oscillatory, "
            f"{PRED_SPEED_SEGMENTS} segments)"
        ),
    }

    info_str = (
        f"Step: {step} | Mode: {mode_text[PRED_SPEED_MODE]} | "
        f"Speed: {predator_speed:.2f} | "
        f"Prey count: {current_prey_count}"
    )

    draw.text(
        (50, HEIGHT + 10),
        info_str,
        fill=(0, 0, 0),
        font=font,
    )

    img_np = np.array(new_img)
    return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)


# ============================================================
# Main simulation
# ============================================================

print("Starting simulation...")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO),
    fourcc,
    VIDEO_FPS,
    (WIDTH, HEIGHT + TEXT_AREA_HEIGHT),
)

if not video_writer.isOpened():
    raise RuntimeError(
        "Could not open the MP4 video writer. "
        "Check your OpenCV installation."
    )

for step in range(STEPS + 1):
    current_pred_speed = get_predator_speed(step)
    pred_speed_history.append(current_pred_speed)

    if step % FRAME_INTERVAL == 0:
        frame = render_frame(
            prey_pos,
            pred_pos,
            step,
            current_pred_speed,
            len(prey_pos),
        )
        video_writer.write(frame)
        print(
            f"Rendered step {step}, "
            f"predator speed {current_pred_speed:.2f}, "
            f"prey count {len(prey_pos)}"
        )

    if step == STEPS:
        break

    # 1. Prey movement
    move_prey(prey_pos, PREY_SPEED)
    apply_boundary(prey_pos)

    # 2. Predator active Brownian motion
    pred_pos, pred_angles = active_move_pred(
        pred_pos,
        pred_angles,
        speed=current_pred_speed,
        active_diff=ACTIVE_DIFFUSION,
        rot_diff=ROTATIONAL_DIFFUSION,
        dt=DT,
    )
    apply_boundary(pred_pos)

    # 3. Predation
    prey_pos = predation(pred_pos, prey_pos)

    # 4. Record data
    prey_count.append(len(prey_pos))

    for i in range(N_PRED):
        pred_trajectories[i].append(pred_pos[i].copy())

    if (step + 1) % 500 == 0:
        print(
            f"Step {step + 1}: remaining prey {len(prey_pos)}, "
            f"predator speed {current_pred_speed:.2f}"
        )

video_writer.release()
print(f"Video saved to {OUTPUT_VIDEO}")


# ============================================================
# Plot predator trajectories
# ============================================================

print("Plotting predator trajectories...")

plt.figure(figsize=(10, 10))
plt.xlim(0, WIDTH)
plt.ylim(0, HEIGHT)
plt.xlabel("x")
plt.ylabel("y")
plt.title("Predator Trajectories (Active Brownian Motion)")

colors = plt.cm.jet(np.linspace(0, 1, N_PRED))
for i, traj in enumerate(pred_trajectories):
    traj = np.array(traj)
    plt.plot(
        traj[:, 0],
        traj[:, 1],
        color=colors[i],
        linewidth=0.5,
        alpha=0.7,
    )

plt.savefig(OUTPUT_TRAJECTORY_PNG, dpi=150)
plt.close()
print(f"Trajectory plot saved to {OUTPUT_TRAJECTORY_PNG}")


# ============================================================
# Plot prey count
# ============================================================

print("Plotting prey count over time...")

plt.figure(figsize=(10, 6))
plt.plot(
    range(STEPS + 1),
    prey_count,
    color="blue",
    linewidth=1,
)
plt.xlabel("Step")
plt.ylabel("Number of Prey")
plt.title("Prey Population Over Time")
plt.grid(alpha=0.3)
plt.savefig(OUTPUT_COUNT_PNG, dpi=150)
plt.close()
print(f"Prey count plot saved to {OUTPUT_COUNT_PNG}")


# ============================================================
# Export CSV files
# ============================================================

print("Exporting prey count CSV...")

with open(OUTPUT_COUNT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "prey_count"])
    for step, count in enumerate(prey_count):
        writer.writerow([step, count])


print("Exporting predator trajectories (long format)...")

with open(OUTPUT_TRAJECTORY_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "predator_id", "x", "y"])

    for i, traj in enumerate(pred_trajectories):
        for step, (x, y) in enumerate(traj):
            writer.writerow([step, i, x, y])


print("Exporting predator trajectories (wide format)...")

traj_array = np.array(
    [np.array(traj) for traj in pred_trajectories]
)
traj_array = np.transpose(traj_array, (1, 0, 2))

with open(OUTPUT_TRAJECTORY_WIDE_CSV, "w", newline="") as f:
    header = ["step"]

    for i in range(N_PRED):
        header.append(f"pred{i}_x")
        header.append(f"pred{i}_y")

    writer = csv.writer(f)
    writer.writerow(header)

    for step in range(STEPS + 1):
        row = [step]

        for i in range(N_PRED):
            row.append(traj_array[step, i, 0])
            row.append(traj_array[step, i, 1])

        writer.writerow(row)


print("Exporting predator speed CSV...")

with open(OUTPUT_SPEED_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "predator_speed"])

    for step, speed in enumerate(pred_speed_history):
        writer.writerow([step, speed])


print("Calculating predator MSD...")

init_pos = np.array(
    [pred_trajectories[i][0] for i in range(N_PRED)]
)

msd_list = []

for step in range(STEPS + 1):
    curr_pos = np.array(
        [pred_trajectories[i][step] for i in range(N_PRED)]
    )
    squared_displacement = np.sum(
        (curr_pos - init_pos) ** 2,
        axis=1,
    )
    msd_list.append(np.mean(squared_displacement))

with open(OUTPUT_MSD_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "msd"])

    for step, msd in enumerate(msd_list):
        writer.writerow([step, msd])


print("All tasks completed.")
print(f"All results are stored in: {OUTPUT_DIR.resolve()}")
