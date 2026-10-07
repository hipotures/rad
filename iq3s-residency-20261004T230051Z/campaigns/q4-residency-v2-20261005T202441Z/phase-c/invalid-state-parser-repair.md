# Invalid state classification repair

Before primary measured cells began, main_matrix.py was corrected to recognize the shared harness state INVALID_PROTOCOL as a retained invalid attempt as well as INVALID. This does not change any request or runtime; it avoids treating a recorded EOS/protocol invalidity as an unrecorded engine crash. Such attempts remain excluded and count toward three total attempts. No replacement repeats.
