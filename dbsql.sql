CREATE TABLE settings (channel_id STRING PRIMARY KEY UNIQUE NOT NULL, current_num INTEGER DEFAULT (0));
CREATE TABLE videos (video_id STRING PRIMARY KEY NOT NULL UNIQUE, played_at DATETIME DEFAULT (0), num_plays INTEGER DEFAULT (0), video_length INTEGER NOT NULL, title STRING NOT NULL, threeD BOOLEAN DEFAULT (FALSE) NOT NULL, views INTEGER NOT NULL, date_published DATE NOT NULL, likes INTEGER NOT NULL, dislikes INTEGER NOT NULL);
