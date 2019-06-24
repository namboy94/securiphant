# Scenarios

# Coming Home

1. Open door
2. Door Sensor notices open door
3. Authentication Timer is started (15s)
4. Start recording video from webcam
5. User authenticates using NFC tag (or smartphone if possible)
6. Store ```is_home=True``` in database
7. Stop authentication timer
8. Delete recorded video
9. Say "Welcome Home" via Loudspeaker

# Break-in

1. Open door
2. Door Sensor notices open door
3. Authentication Timer is started (15s)
4. Start recording video from webcam
5. Authentication Timer runs out
6. Save Video to file.
7. Extract image at 1s, 7s, 14s from video
8. Send images using Telegram (powered by kudubot)
9. Send video using telegram
10. Start recording new 30s videos in perpetuity until authenticated.
11. Send each 30s video using telegram
12. Authenticate using NFC tag
13. Store ```is_home=True``` in database
14. Stop authentication timer
15. Stop recording video
16. Don't delete recorded videos
17. Say "We may have had a break-in" via Loudspeaker