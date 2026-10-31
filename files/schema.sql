CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  student_id TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'voter'
);

CREATE TABLE IF NOT EXISTS elections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  is_open INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  election_id INTEGER NOT NULL REFERENCES elections(id),
  name TEXT NOT NULL,
  position TEXT
);

-- WHO has voted (no choice stored)
CREATE TABLE IF NOT EXISTS ballots_cast (
  election_id INTEGER NOT NULL,
  voter_id INTEGER NOT NULL,
  PRIMARY KEY (election_id, voter_id)
);

-- WHAT was voted (no voter stored)
CREATE TABLE IF NOT EXISTS votes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  election_id INTEGER NOT NULL,
  candidate_id INTEGER NOT NULL REFERENCES candidates(id)
);
