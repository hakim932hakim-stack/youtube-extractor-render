FROM python:3.11-slim

WORKDIR /app

# ffmpeg ve yt-dlp kur
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install yt-dlp flask gunicorn

COPY server.py /app/

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--timeout", "60", "server:app"]
