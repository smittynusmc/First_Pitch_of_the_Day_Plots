import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import requests
import threading
import queue
import matplotlib

matplotlib.use('TkAgg')  # Use the TkAgg backend

# Queue for GUI updates
update_queue = queue.Queue()

def process_queue():
    if root.winfo_exists():
        try:
            task = update_queue.get_nowait()
            task()
        except queue.Empty:
            pass
        root.after(100, process_queue)  # Continue checking every 100 ms
    else:
        print("Root window no longer exists.")


def fetch_play_by_play(api_key, game_id):
    """Fetch play-by-play data for a specified game."""
    url = f"https://api.sportradar.com/mlb/trial/v7/en/games/{game_id}/pbp.json?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch play-by-play data: {response.status_code}")
        return None

def fetch_mlb_schedule(api_key, year, month, day):
    """Fetch MLB game schedule for a specific date."""
    url = f"https://api.sportradar.com/mlb/trial/v7/en/games/{year}/{month}/{day}/schedule.json?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch schedule data: {response.status_code}")
        return None

def extract_first_pitch(innings):
    """Extract the first pitch event from innings data."""
    for inning in innings:
        if inning['number'] == 1:
            for half in inning['halfs']:
                for event in half['events']:
                    if 'at_bat' in event and 'events' in event['at_bat']:
                        for pitch_event in event['at_bat']['events']:
                            if pitch_event['type'] == 'pitch':
                                return pitch_event
    return None

def visualize_strike_zone(pitch, game_date, teams, location):
    # Initialize the figure and axis early to ensure they exist regardless of errors
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        # Extract necessary data
        x = pitch['mlb_pitch_data']['coordinates']['x']
        y = pitch['mlb_pitch_data']['coordinates']['y']
        pitch_type = pitch['pitcher']['pitch_type']
        pitch_speed = pitch['pitcher']['pitch_speed']
        pitcher_name = pitch['pitcher']['full_name']
        hitter_name = pitch['hitter']['full_name']

        # Draw the strike zone rectangle
        strike_zone = patches.Rectangle((0.35, 0.3), 0.3, 0.4, color='red', linewidth=2, fill=False)
        ax.add_patch(strike_zone)

        # Normalize and plot the pitch location
        normalized_x = (x - 100) / 100 * 0.3 + 0.35
        normalized_y = (y - 100) / 100 * 0.4 + 0.3
        ax.plot(normalized_x, normalized_y, 'ro')

        # Add text for game info and pitch details
        ax.text(0.5, 1.1, f"Date: {game_date}\nMatchup: {teams}\nLocation: {location}", ha='center', va='top', fontsize=8, transform=ax.transAxes, color='green')
        ax.text(0.5, 0, f'Pitcher: {pitcher_name} vs. Hitter: {hitter_name}\nPitch Type: {pitch_type} @ {pitch_speed} mph', ha='center', va='bottom', fontsize=8, transform=ax.transAxes, color='blue')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')

    except KeyError as e:
        print(f"Key error in visualization function: {e}")
        ax.text(0.5, 0.5, "Visualization Error", ha='center', va='center', color='red')
    except Exception as e:
        print(f"An error occurred: {e}")
        ax.text(0.5, 0.5, "Unexpected Error", ha='center', va='center', color='red')

    return fig, ax  # This line ensures that even in error cases, something is returned


def threaded_visualization(api_key, year, month, day, button):
    try:
        schedule = fetch_mlb_schedule(api_key, year, month, day)
        if schedule and 'games' in schedule:
            for game in schedule['games']:
                # Processing data here, ensure it's thread-safe
                handle_game_data(api_key, game)
        else:
            update_queue.put(lambda: messagebox.showinfo("Error", "Failed to fetch game schedule or no games found."))
    except Exception as e:
        error_message = str(e)
        update_queue.put(lambda e=error_message: messagebox.showerror("Error", f"An error occurred: {e}"))
    finally:
        # Push GUI updates to the main thread via queue
        update_queue.put(lambda: [progress_bar.stop(), button.config(state=tk.NORMAL)])

def handle_game_data(api_key, game):
    game_date = game['scheduled'][:10]  # Format: YYYY-MM-DD
    teams = f"{game['away']['name']} vs {game['home']['name']}"
    location = game['venue']['name']
    play_by_play = fetch_play_by_play(api_key, game['id'])
    if play_by_play and 'game' in play_by_play:
        innings = play_by_play['game'].get('innings', [])
        first_pitch = extract_first_pitch(innings)
        if first_pitch:
            fig, ax = visualize_strike_zone(first_pitch, game_date, teams, location)
            tab = ttk.Frame(notebook)
            update_queue.put(lambda: [notebook.add(tab, text=f"{teams}"), display_figure(fig, ax, tab)])
        else:
            update_queue.put(lambda: messagebox.showinfo("Info", "No first pitch data available for " + teams))
    else:
        update_queue.put(lambda: messagebox.showinfo("Error", "Failed to fetch play-by-play data for " + teams))


def display_figure(fig, ax, tab):
    """Display figure on a notebook tab."""
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    plt.close(fig)  # Close the figure to release memory

def handle_load_button_press(api_key, year, month, day, button):
    # Start the progress bar before launching the thread
    progress_bar.start(10)  # Start with a small step to show activity
    button.config(state=tk.DISABLED)  # Disable button to prevent multiple presses
    # Launch the thread to perform data fetching
    threading.Thread(target=threaded_visualization, args=(api_key, year, month, day, button)).start()


def create_gui(api_key):
    """Create the main GUI window."""
    global root, notebook, progress_bar
    root = tk.Tk()
    root.title("MLB Game Data Viewer")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, fill=tk.X)

    tk.Label(frame, text="Year:").pack(side=tk.LEFT)
    year_entry = tk.Entry(frame, width=7)
    year_entry.pack(side=tk.LEFT)

    tk.Label(frame, text="Month:").pack(side=tk.LEFT)
    month_entry = tk.Entry(frame, width=5)
    month_entry.pack(side=tk.LEFT)

    tk.Label(frame, text="Day:").pack(side=tk.LEFT)
    day_entry = tk.Entry(frame, width=5)
    day_entry.pack(side=tk.LEFT)

    action_button = tk.Button(frame, text="Load Game Data", command=lambda: threaded_visualization(api_key, year_entry.get(), month_entry.get(), day_entry.get(), action_button))
    action_button.pack(side=tk.LEFT)

    quit_button = tk.Button(frame, text="End Program", command=root.quit)
    quit_button.pack(side=tk.RIGHT)

    progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
    progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    root.after(100, process_queue)
    root.mainloop()

if __name__ == "__main__":
    api_key = 'spzA1Ipyju3FsEb7LzmEK7NzCAQ34msD8E3JMwP1'
    create_gui(api_key)
