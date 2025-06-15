from typing import Optional, List
from passlib.context import CryptContext
from trm_api.graph_models.user import User as GraphUser
from trm_api.models.user import UserCreate, UserUpdate # Pydantic model for API data

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    """
    Repository for handling all database operations related to Users.
    """

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_user(self, user_data: UserCreate) -> GraphUser:
        """
        Creates a new User node in the database with a hashed password.
        """
        try:
            # Create a dictionary from the pydantic model
            user_dict = user_data.model_dump()
            # Hash the password before saving
            user_dict["hashed_password"] = self.get_password_hash(user_dict.pop("password"))
            
            print(f"DEBUG - Tạo User với dữ liệu: {user_dict}")
            
            # Kiểm tra xem Neo4j có kết nối được không
            from neomodel import db
            results, meta = db.cypher_query("MATCH (n) RETURN COUNT(n) LIMIT 1")
            print(f"DEBUG - Kết nối Neo4j OK, số node hiện tại: {results[0][0]}")
            
            graph_user = GraphUser(**user_dict).save()
            print(f"DEBUG - Đã tạo User thành công: {graph_user.username}")
            return graph_user
        except Exception as e:
            import traceback
            print(f"ERROR - Lỗi khi tạo User: {str(e)}")
            print(traceback.format_exc())
            raise

    def get_user_by_username(self, username: str) -> Optional[GraphUser]:
        """
        Retrieves a User node by their username.
        """
        try:
            return GraphUser.nodes.get(username=username)
        except GraphUser.DoesNotExist:
            return None

    def get_user_by_email(self, email: str) -> Optional[GraphUser]:
        """
        Retrieve a user by email.
        """
        try:
            return GraphUser.nodes.get(email=email)
        except GraphUser.DoesNotExist:
            return None

    def get_user_by_uid(self, uid: str) -> Optional[GraphUser]:
        """
        Retrieves a User node by its unique ID.
        """
        try:
            return GraphUser.nodes.get(uid=uid)
        except GraphUser.DoesNotExist:
            return None

    def list_users(self, skip: int = 0, limit: int = 100) -> List[GraphUser]:
        """
        Retrieves a list of all users with pagination.
        """
        print(f"DEBUG - UserRepository.list_users: Bắt đầu lấy danh sách người dùng. Skip: {skip}, Limit: {limit}")
        try:
            from neomodel import db
            # Kiểm tra kết nối nhanh
            db.cypher_query("MATCH (n:User) RETURN count(n) AS user_count")
            print(f"DEBUG - UserRepository.list_users: Kết nối Neo4j và truy vấn kiểm tra thành công.")
            
            all_users_node_set = GraphUser.nodes.all()
            print(f"DEBUG - UserRepository.list_users: Đã gọi GraphUser.nodes.all(). Số lượng (ước tính): {len(all_users_node_set)}")
            
            users = all_users_node_set[skip:skip + limit]
            print(f"DEBUG - UserRepository.list_users: Đã cắt danh sách. Số lượng sau khi cắt: {len(users)}")
            
            # Chuyển đổi sang danh sách để đảm bảo không có vấn đề lazy loading
            user_list = list(users)
            print(f"DEBUG - UserRepository.list_users: Hoàn thành, trả về {len(user_list)} người dùng.")
            return user_list
        except Exception as e:
            import traceback
            print(f"ERROR - UserRepository.list_users: Lỗi khi lấy danh sách người dùng: {str(e)}")
            print(traceback.format_exc())
            # Trả về danh sách rỗng trong trường hợp lỗi để tránh treo API
            return []

    def update_user(self, uid: str, user_data: UserUpdate) -> Optional[GraphUser]:
        """
        Updates an existing user.
        Note: Does not support password changes through this method for security.
        """
        user = self.get_user_by_uid(uid)
        if not user:
            return None

        # Use by_alias=True to ensure the dictionary keys match the GraphModel's property names
        update_data = user_data.model_dump(exclude_unset=True, by_alias=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.save()
        return user

    def delete_user(self, uid: str) -> bool:
        """
        Deletes a user by their unique ID.
        """
        user = self.get_user_by_uid(uid)
        if not user:
            return False
        
        user.delete()
        return True
