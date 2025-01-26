import psycopg2 # type: ignore
import logging
import os
import json
from datetime import datetime, timedelta
import uuid

# Connessione al database SQLite
def connect_db():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="db",
        port="5432"
    )

# Funzioni CRUD per Sessions
def create_session(session_id):
    conn = connect_db()
    cursor = conn.cursor()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Session INSERT")
    query = """
        INSERT INTO Session (session_id, created_at)
        VALUES (%s, %s)
    """
    print(query)
    cursor.execute(query, (session_id, created_at))
    print(f"Session created: {session_id}")
    conn.commit()
    conn.close()
    return session_id

def read_session(session_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Session WHERE session_id = %s", (session_id,))
    session = cursor.fetchone()
    conn.close()
    return session

# Funzioni CRUD per Conversations
def create_conversation(session_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Conversation (session_id, created_at)
        VALUES (%s, CURRENT_TIMESTAMP)
        RETURNING conversation_id
    """, (session_id,))
    conversation_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return conversation_id

def read_conversations(session_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Conversation WHERE session_id = %s", (session_id,))
    conversations = cursor.fetchall()
    conn.close()
    return [{
        'conversation_id': conv[0]
    } for conv in conversations]

def read_conversation_by_id(conversation_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Conversation WHERE conversation_id = %s", (conversation_id,))
    conversations = cursor.fetchall()
    conn.close()
    return conversations

def delete_conversation(conversation_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Conversation WHERE conversation_id = %s", (conversation_id,))
    conn.commit()
    conn.close()

# Funzioni CRUD per Messages
def add_message(conversation_id, sender, content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Message (conversation_id, sender, content, created_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING message_id
    """, (conversation_id, sender, content,))
    message_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return message_id

def read_messages(conversation_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Message WHERE conversation_id = %s", (conversation_id,))
    messages = cursor.fetchall()
    conn.close()
    return [{
        'message_id': message[0],
        'conversation_id': message[1],
        'sender': message[2],
        'content': message[3],
        'created_at': message[4]
    } for message in messages]