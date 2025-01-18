from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from db import Session
from models import (
    Users, Character, Doctor, Enemy, Race, 
    Message, Journey, Character_In_Journey, Time
)

# Инициализация FastAPI
app = FastAPI(title="Doctor Who API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка безопасности
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic модели
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserSignup(BaseModel):
    login: str
    password: str
    name: str
    race: str
    age: int
    relationship: str
    reason: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None

class MessageCreate(BaseModel):
    to_user_id: int
    message: str

class JourneyCreate(BaseModel):
    planet: int
    time: str
    doctor: int
    description: str

class CharacterResponse(BaseModel):
    id: int
    name: str
    age: int
    state: str
    relationship: str

# Вспомогательные функции
def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    session = Session()
    try:
        user = session.query(Users).filter_by(login=login).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    finally:
        session.close()

# Маршруты
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    session = Session()
    try:
        user = session.query(Users).filter_by(login=form_data.username).first()
        if not user or not pwd_context.verify(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": user.login, "exp": access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        session.close()

@app.get("/characters/{id}", response_model=Dict[str, Any])
async def get_character(id: int):
    session = Session()
    try:
        character = session.query(Character).filter_by(id=id).first()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )

        race = session.query(Race).filter_by(id=character.race_id).first()
        user = session.query(Users).filter_by(character_id=character.id).first()

        result = {
            'name': character.name,
            'age': character.age,
            'state': character.state,
            'relationship': character.relationship,
            'user_id': user.id if user else None,
            'race': race.name
        }

        if character.relationship == 'doctor':
            doctor = session.query(Doctor).filter_by(character_id=character.id).first()
            result.update({
                'appearance': doctor.appearance,
                'personality': doctor.personality
            })
        elif character.relationship == 'enemy':
            enemy = session.query(Enemy).filter_by(character_id=character.id).first()
            result['reason'] = enemy.reason

        return result
    finally:
        session.close()

@app.get("/characters", response_model=List[CharacterResponse])
async def get_characters():
    session = Session()
    try:
        characters = session.query(Character).all()
        return [
            CharacterResponse(
                id=char.id,
                name=char.name,
                age=char.age,
                state=char.state,
                relationship=char.relationship
            )
            for char in characters
        ]
    finally:
        session.close()

@app.get("/journeys", response_model=List[Dict[str, Any]])
async def get_journeys(current_user: Users = Depends(get_current_user)):
    session = Session()
    try:
        journeys = session.query(Journey, Time).\
            join(Character_In_Journey, Character_In_Journey.journey_id == Journey.id).\
            join(Time, Time.id == Journey.time_id).\
            filter(Character_In_Journey.character_id == current_user.character_id).\
            all()
        
        return [{
            'id': journey.id,
            'planet_id': journey.planet_id,
            'time': time.timerfbuinverse,
            'doctor_id': journey.doctor_id,
            'description': journey.description
        } for journey, time in journeys]
    finally:
        session.close()

@app.post("/add_journey", status_code=status.HTTP_201_CREATED)
async def add_journey(
    journey_data: JourneyCreate,
    current_user: Users = Depends(get_current_user)
):
    session = Session()
    try:
        new_time = Time(
            timerfbuinverse=journey_data.time,
            timerfbplanet=journey_data.time
        )
        session.add(new_time)
        session.flush()

        new_journey = Journey(
            planet_id=journey_data.planet,
            time_id=new_time.id,
            doctor_id=journey_data.doctor,
            description=journey_data.description
        )
        session.add(new_journey)
        session.flush()

        new_character_in_journey = Character_In_Journey(
            character_id=current_user.character_id,
            journey_id=new_journey.id
        )
        session.add(new_character_in_journey)
        
        session.commit()
        return {"message": "Journey added successfully", "journey_id": new_journey.id}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create journey: {str(e)}"
        )
    finally:
        session.close()

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    session = Session()
    try:
        # Проверяем существование пользователя
        if session.query(Users).filter_by(login=user_data.login).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
            
        # Создаем персонажа
        character = Character(
            name=user_data.name,
            age=user_data.age,
            state="alive",
            relationship=user_data.relationship
        )
        session.add(character)
        session.flush()
        
        # Создаем пользователя
        hashed_password = pwd_context.hash(user_data.password)
        new_user = Users(
            login=user_data.login,
            password_hash=hashed_password,
            character_id=character.id
        )
        session.add(new_user)
        session.commit()
        
        return {"message": "User created successfully", "user_id": new_user.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 
