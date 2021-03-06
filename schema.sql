CREATE DATABASE photoshare;
USE photoshare;

-- CREATE USER TABLE
CREATE TABLE USERS (
    UID INT NOT NULL AUTO_INCREMENT,
    GENDER VARCHAR(6),
    EMAIL VARCHAR(40) UNIQUE,
    PASSWORD VARCHAR(40) NOT NULL,
    DOB DATE,
    HOMETOWN VARCHAR(40),
    FNAME VARCHAR(40) NOT NULL,
    LNAME VARCHAR(40) NOT NULL,
    PRIMARY KEY (uid)
);

-- CREATE FRIENDSHIP TABLE
CREATE TABLE FRIENDSHIP(
	UID1 INT NOT NULL,
	UID2 INT NOT NULL,
	PRIMARY KEY(UID1, UID2),
	FOREIGN KEY (UID1) REFERENCES Users(UID) ON DELETE CASCADE,
	FOREIGN KEY (UID2) REFERENCES Users(UID) ON DELETE CASCADE
);


-- CREATE Album TABLE (include album entity and 'own' relationship)
CREATE TABLE ALBUM(
	AID INT AUTO_INCREMENT,
	A_NAME VARCHAR(40) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PRIMARY KEY (AID),
	FOREIGN KEY (UID) REFERENCES Users(UID) ON DELETE CASCADE
);

-- CREATE Photo TABLE (include photo entity and 'contains' relationship)
CREATE TABLE PHOTO(
	PID INT AUTO_INCREMENT,
	CAPTION VARCHAR(200),
	IMG_DATA BLOB NOT NULL,
	AID INT NOT NULL,
  UID INT NOT NULL,
	PRIMARY KEY (PID),
	FOREIGN KEY (AID) REFERENCES ALBUM(AID) ON DELETE CASCADE,
  FOREIGN KEY (UID) REFERENCES Users(UID) ON DELETE CASCADE
);

-- CREATE Comment TABLE (include comment entity and 'comment' relationship)
CREATE TABLE COMMENT(
	CID INT NOT NULL AUTO_INCREMENT,
	CONTENT VARCHAR(200) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PID INT NOT NULL,
	PRIMARY KEY (CID),
	FOREIGN KEY (UID) REFERENCES USERS(UID) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

-- CREATE THE LIKETABLE. WE CAN'T name it LIKE
CREATE TABLE LIKETABLE(
	UID INT NOT NULL,
	PID INT NOT NULL,
	DOC TIMESTAMP NOT NULL,
        PRIMARY KEY (UID, PID),
	FOREIGN KEY (UID) REFERENCES USERS(UID) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);


-- CREATE Tag TABLE
CREATE TABLE TAG(
	HASHTAG VARCHAR(40) NOT NULL,
	PRIMARY KEY (HASHTAG)
);

-- CREATE Associate Table
CREATE TABLE ASSOCIATE(
	PID INT NOT NULL,
	HASHTAG VARCHAR(40) NOT NULL,
        PRIMARY KEY (PID, HASHTAG),
	FOREIGN KEY (HASHTAG) REFERENCES TAG(HASHTAG) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);
