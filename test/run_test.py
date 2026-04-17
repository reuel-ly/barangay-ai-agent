import subprocess

batch_size = 5
total_samples = 10
metric_amount = 3



for start in range(0, total_samples, batch_size):
    for idx in range(metric_amount):
        end = start + batch_size

        print(f"\n[Running batch {start} to {end}]")

        subprocess.run([
            "python", "-m", "test.ragas_eval",
            "--start", str(start),
            "--end", str(end),
            "--idx", str(idx)
        ])