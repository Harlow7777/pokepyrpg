import pygame
import time

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self._current_track = None
        self._previous_track = None
        self._pending_track = None
        self._fade_complete_time = None

    def play_music(self, track_path, loop=True, fadeout_ms=0, volume=1.0):
        if self._current_track == track_path:
            return

        if self._current_track != track_path:
            self._previous_track = self._current_track

        if fadeout_ms > 0 and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fadeout_ms)
            self._pending_track = (track_path, loop, volume)
            self._fade_complete_time = pygame.time.get_ticks() + fadeout_ms
            return

        self._start_music(track_path, loop, volume)

    def _start_music(self, track_path, loop, volume):
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        self._current_track = track_path
        self._pending_track = None
        self._fade_complete_time = None

    def update_music(self):
        if self._pending_track and pygame.time.get_ticks() >= self._fade_complete_time:
            track_path, loop, volume = self._pending_track
            self._start_music(track_path, loop, volume)

    def resume_previous_music(self, fadeout_ms=0):
        if self._previous_track:
            self.play_music(self._previous_track, fadeout_ms=fadeout_ms)
