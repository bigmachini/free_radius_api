import logging

from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional

from db_config import get_db_connection, db_pool
from models import User, MACAddress, AccountingStart, AccountingStop

app = FastAPI()


@app.get("/users", response_model=List[User])
def get_all_users():
    query = "SELECT * FROM radcheck ORDER BY id;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db_pool.putconn(conn)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving users") from e


@app.get("/user/{username}", response_model=Optional[User])
def get_user_by_username(username: str):
    query = "SELECT * FROM radcheck WHERE username = %s;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        db_pool.putconn(conn)
        if result:
            return result
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving user") from e


@app.post("/user")
def add_user(user: User):
    query = """
        INSERT INTO radcheck (username, attribute, op, value)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (user.username, user.attribute, user.op, user.value))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        db_pool.putconn(conn)
        return {"message": "User added successfully", "id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error adding user") from e


@app.put("/user/{username}")
def update_user(username: str, user: User):
    query = """
        UPDATE radcheck
        SET attribute = %s, op = %s, value = %s
        WHERE username = %s
        RETURNING id;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (user.attribute, user.op, user.value, username))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        db_pool.putconn(conn)
        if result:
            return {"message": "User updated successfully", "id": result["id"]}
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error updating user") from e


@app.delete("/user/{username}")
def delete_user(username: str):
    query = "DELETE FROM radcheck WHERE username = %s RETURNING id;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        db_pool.putconn(conn)
        if result:
            return {"message": "User deleted successfully", "id": result["id"]}
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting user") from e


# Accounting Endpoints

@app.post("/accounting/start")
def accounting_start(data: AccountingStart):
    """
    Handle Accounting Start packets.
    """
    query = """
    INSERT INTO radacct (
        acctsessionid, acctuniqueid, username, nasipaddress, calledstationid,
        callingstationid, framedipaddress, servicetype, framedprotocol, acctstarttime
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    RETURNING radacctid;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            query,
            (
                data.acctsessionid,
                data.acctuniqueid,
                data.username,
                data.nasipaddress,
                data.calledstationid,
                data.callingstationid,
                data.framedipaddress,
                data.servicetype,
                data.framedprotocol,
            ),
        )
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Accounting start recorded", "radacctid": result["radacctid"]}
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Error recording accounting start") from e


@app.post("/accounting/stop")
def accounting_stop(data: AccountingStop):
    """
    Handle Accounting Stop packets.
    """
    query = """
    UPDATE radacct
    SET acctstoptime = NOW(),
        acctsessiontime = %s,
        acctinputoctets = %s,
        acctoutputoctets = %s,
        acctterminatecause = %s
    WHERE acctsessionid = %s AND acctuniqueid = %s
    RETURNING radacctid;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            query,
            (
                data.acctsessiontime,
                data.acctinputoctets,
                data.acctoutputoctets,
                data.acctterminatecause,
                data.acctsessionid,
                data.acctuniqueid,
            ),
        )
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if result:
            return {"message": "Accounting stop recorded", "radacctid": result["radacctid"]}
        raise HTTPException(status_code=404, detail="Session not found")
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Error recording accounting stop") from e


@app.get("/accounting/sessions", response_model=List[dict])
def get_all_sessions():
    """
    Retrieve all accounting sessions.
    """
    query = "SELECT * FROM radacct ORDER BY acctstarttime DESC;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Error retrieving sessions") from e


@app.get("/accounting/session/{acctsessionid}")
def get_session_by_id(acctsessionid: str):
    """
    Retrieve an accounting session by session ID.
    """
    query = "SELECT * FROM radacct WHERE acctsessionid = %s;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, (acctsessionid,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result
        raise HTTPException(status_code=404, detail="Session not found")
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Error retrieving session") from e
