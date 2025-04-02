from flask import Flask, render_template_string, request
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import random

app = Flask(__name__)

def generate_random_requests(total_cylinders, num_requests=8):
    return sorted(random.sample(range(total_cylinders), num_requests))

def fcfs_schedule(requests, head_pos):
    return [head_pos] + requests

def sstf_schedule(requests, head_pos):
    schedule = [head_pos]
    remaining = requests.copy()
    current_pos = head_pos
    
    while remaining:
        closest = min(remaining, key=lambda x: abs(x - current_pos))
        schedule.append(closest)
        current_pos = closest
        remaining.remove(closest)
    
    return schedule

def scan_schedule(requests, head_pos, total_cylinders, direction="right"):
    schedule = [head_pos]
    requests_sorted = sorted(requests)
    
    left = [r for r in requests_sorted if r <= head_pos]
    right = [r for r in requests_sorted if r > head_pos]
    
    if direction == "right":
        schedule += right
        if right:
            schedule.append(total_cylinders - 1)
        schedule += left[::-1]
    else:
        schedule += left[::-1]
        if left:
            schedule.append(0)
        schedule += right
    
    return schedule

def cscan_schedule(requests, head_pos, total_cylinders, direction="right"):
    schedule = [head_pos]
    requests_sorted = sorted(requests)
    
    left = [r for r in requests_sorted if r <= head_pos]
    right = [r for r in requests_sorted if r > head_pos]
    
    if direction == "right":
        schedule += right
        if right:
            schedule.append(total_cylinders - 1)
            schedule.append(0)
        schedule += left
    else:
        schedule += left[::-1]
        if left:
            schedule.append(0)
            schedule.append(total_cylinders - 1)
        schedule += right[::-1]
    
    return schedule

def look_schedule(requests, head_pos, direction="right"):
    schedule = [head_pos]
    requests_sorted = sorted(requests)
    
    left = [r for r in requests_sorted if r <= head_pos]
    right = [r for r in requests_sorted if r > head_pos]
    
    if direction == "right":
        if right:
            schedule += right
        if left:
            schedule += left[::-1]
    else:
        if left:
            schedule += left[::-1]
        if right:
            schedule += right
    
    return schedule

def clook_schedule(requests, head_pos, direction="right"):
    schedule = [head_pos]
    requests_sorted = sorted(requests)
    
    left = [r for r in requests_sorted if r <= head_pos]
    right = [r for r in requests_sorted if r > head_pos]
    
    if direction == "right":
        if right:
            schedule += right
        if left:
            schedule.append(min(requests))
            schedule += left[1:] if len(left) > 1 else []
    else:
        if left:
            schedule += left[::-1]
        if right:
            schedule.append(max(requests))
            schedule += right[-2::-1] if len(right) > 1 else []
    
    return schedule

def plot_schedule(schedule, requests, total_cylinders, algorithm):
    plt.figure(figsize=(10, 3))
    plt.xlim(0, total_cylinders)
    plt.ylim(0, 3)
    plt.yticks([])
    plt.xlabel("Cylinder Number")
    plt.title(f"{algorithm} Disk Scheduling")
    
    # Draw disk cylinders
    for i in range(0, total_cylinders, 10):
        plt.axvline(i, color='gray', alpha=0.2)
    
    # Plot requests
    for req in requests:
        plt.plot(req, 1, 'ro', markersize=8)
    
    # Plot schedule path
    plt.plot(schedule, [2]*len(schedule), 'b-', linewidth=2)
    plt.plot(schedule[-1], 2, 'bo', markersize=10)
    
    # Save plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close()
    img.seek(0)
    
    # Convert to base64 for HTML
    return base64.b64encode(img.read()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        req_text = request.form['requests']
        head_pos = int(request.form['head_pos'])
        total_cylinders = int(request.form['total_cylinders'])
        direction = request.form['direction']
        algorithm = request.form['algorithm']
        
        # Parse requests
        requests = [int(x.strip()) for x in req_text.split(',')]
        
        # Generate schedule
        if algorithm == "FCFS":
            schedule = fcfs_schedule(requests, head_pos)
        elif algorithm == "SSTF":
            schedule = sstf_schedule(requests, head_pos)
        elif algorithm == "SCAN":
            schedule = scan_schedule(requests, head_pos, total_cylinders, direction)
        elif algorithm == "C-SCAN":
            schedule = cscan_schedule(requests, head_pos, total_cylinders, direction)
        elif algorithm == "LOOK":
            schedule = look_schedule(requests, head_pos, direction)
        elif algorithm == "C-LOOK":
            schedule = clook_schedule(requests, head_pos, direction)
        
        # Calculate total seek operations
        total_seek = sum(abs(schedule[i+1] - schedule[i]) for i in range(len(schedule)-1))
        
        # Generate plot
        plot_url = plot_schedule(schedule, requests, total_cylinders, algorithm)
        
        # Render results
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Disk Scheduling Results</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .container { max-width: 900px; margin: auto; }
                    .results { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                    img { max-width: 100%; height: auto; }
                    .form-group { margin-bottom: 10px; }
                    label { display: inline-block; width: 180px; }
                    input, select { padding: 5px; width: 200px; }
                    button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Disk Scheduling Results</h1>
                    
                    <div class="results">
                        <h2>Algorithm: {{ algorithm }}</h2>
                        <p><strong>Initial Head Position:</strong> {{ head_pos }}</p>
                        <p><strong>Request Queue:</strong> {{ requests }}</p>
                        <p><strong>Schedule Order:</strong> {{ schedule }}</p>
                        <p><strong>Total Seek Operations:</strong> {{ total_seek }}</p>
                        <p><strong>Direction:</strong> {{ direction }}</p>
                        
                        <img src="data:image/png;base64,{{ plot_url }}" alt="Disk Scheduling Visualization">
                    </div>
                    
                    <p><a href="/">Back to Simulator</a></p>
                </div>
            </body>
            </html>
        ''', algorithm=algorithm, head_pos=head_pos, requests=requests, 
           schedule=schedule, total_seek=total_seek, direction=direction, 
           plot_url=plot_url)
    
    # Default form (GET request)
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Disk Scheduling Simulator</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 500px; margin: auto; }
                .form-group { margin-bottom: 10px; }
                label { display: inline-block; width: 180px; }
                input, select { padding: 5px; width: 200px; }
                button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Disk Scheduling Simulator</h1>
                
                <form method="POST">
                    <div class="form-group">
                        <label for="requests">Request Queue (comma-separated):</label>
                        <input type="text" id="requests" name="requests" value="98, 183, 37, 122, 14, 124, 65, 67" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="head_pos">Initial Head Position:</label>
                        <input type="number" id="head_pos" name="head_pos" value="53" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="total_cylinders">Total Cylinders:</label>
                        <input type="number" id="total_cylinders" name="total_cylinders" value="200" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Initial Direction:</label>
                        <input type="radio" id="right" name="direction" value="right" checked>
                        <label for="right" style="width: auto;">Right</label>
                        <input type="radio" id="left" name="direction" value="left">
                        <label for="left" style="width: auto;">Left</label>
                    </div>
                    
                    <div class="form-group">
                        <label for="algorithm">Scheduling Algorithm:</label>
                        <select id="algorithm" name="algorithm" required>
                            <option value="FCFS">FCFS</option>
                            <option value="SSTF">SSTF</option>
                            <option value="SCAN">SCAN</option>
                            <option value="C-SCAN">C-SCAN</option>
                            <option value="LOOK">LOOK</option>
                            <option value="C-LOOK">C-LOOK</option>
                        </select>
                    </div>
                    
                    <button type="submit">Run Simulation</button>
                </form>
            </div>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
