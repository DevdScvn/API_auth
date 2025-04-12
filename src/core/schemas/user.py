from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    # model_config = ConfigDict(
    #     from_attributes=True
    # )

    id: int


class UserDelete(BaseModel):
    id: int


class UserAuth(BaseModel):
    email: EmailStr
    password: str
