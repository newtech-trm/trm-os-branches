from neo4j import Driver
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import traceback
import uuid

from trm_api.db.session import get_driver
from trm_api.models.win import Win, WinCreate, WinUpdate, WinInDB

class WinService:
    """
    Service layer for handling business logic related to WINs.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def _convert_neo4j_types(self, data: Any) -> Any:
        """Recursively convert Neo4j types to Python native types"""
        logging.debug(f"Converting Neo4j types: {type(data)} - {data}")
        
        # Handle None
        if data is None:
            return None
            
        # Handle dictionary
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                logging.debug(f"Processing dict key {key}: {type(value)} - {value}")
                result[key] = self._convert_neo4j_types(value)
            return result
            
        # Handle list 
        if isinstance(data, list):
            result = []
            for item in data:
                logging.debug(f"Processing list item: {type(item)} - {item}")
                result.append(self._convert_neo4j_types(item))
            return result
            
        # Handle Neo4j DateTime - most important case
        if hasattr(data, 'to_native'):
            logging.debug(f"Converting Neo4j DateTime: {data} to native")
            return data.to_native()
            
        # No conversion needed
        return data

    def create_win(self, win_create: WinCreate) -> Win:
        try:
            logging.debug(f"Creating WIN with data: {win_create}")
            
            # Convert Pydantic model to a regular dictionary
            win_dict = win_create.model_dump()
            logging.debug(f"WIN dict after conversion: {win_dict}")
            
            params = win_dict
            
            logging.debug(f"Creating WIN with params: {params}")

            with self._get_db().session() as session:
                try:
                    # Execute the transaction
                    raw_result = session.write_transaction(self._create_win_tx, win_dict)
                    logging.debug(f"Raw result from Neo4j: {raw_result}")
                    logging.debug(f"Result types: {[(k, type(v)) for k, v in raw_result.items()]}")
                    
                    if not raw_result:
                        logging.error("No result returned from Neo4j transaction")
                        return None
                    # Convert Neo4j types to Python types (especially DateTime)
                    converted_data = self._convert_neo4j_types(raw_result)
                    logging.debug(f"Converted data from Neo4j: {converted_data}")
                    
                    # Handle timestamps specially for reliability
                    for dt_field in ['created_at', 'updated_at']:
                        if dt_field in converted_data and hasattr(converted_data[dt_field], 'to_native'):
                            converted_data[dt_field] = converted_data[dt_field].to_native()
                            logging.debug(f"Specially handling timestamp {dt_field}: {converted_data[dt_field]}")

                    # Create the Win model for validation and return
                    return Win(**converted_data)
                except Exception as e:
                    logging.error(f"Error creating WIN: {e}")
                    raise
        except Exception as e:
            logging.error(f"Error creating WIN: {e}")
            raise

    def _create_win_tx(self, tx, win_data: dict) -> dict:
        """Create a WIN node transaction."""
        create_query = (
            "CREATE (w:WIN {uid: $uid, summary: $summary, description: $description, win_type: $win_type}) "
            "SET w.created_at = datetime(), w.updated_at = datetime() "
            "RETURN w as win"
        )
        
        logging.debug(f"Executing Neo4j query: {create_query} with params: {win_data}")
        
        result = tx.run(
            create_query,
            uid=win_data.get('uid') or str(uuid.uuid4()),
            summary=win_data.get('summary'),
            description=win_data.get('description', ''),
            win_type=win_data.get('win_type', 'standard'),
        )
        
        record = result.single()
        if not record:
            return {}
            
        win_node = record.get('win')
        # Convert Neo4j node to dictionary
        win_data = dict(win_node.items())
        logging.debug(f"WIN data from Neo4j: {win_data}")
        return win_data

    def get_win(self, uid: str) -> Optional[Win]:
        """Get a WIN node by UID."""
        try:
            with self._get_db().session() as session:
                # Execute the query
                raw_result = session.read_transaction(self._get_win_by_uid_tx, uid)
                if not raw_result:
                    return None
                
                # Convert Neo4j types (especially DateTime)
                processed_result = self._convert_neo4j_types(raw_result)
                logging.debug(f"Processed WIN data: {processed_result}")
                
                # Return as a Win model instance
                return Win(**processed_result)
        except Exception as e:
            logging.error(f"Error getting WIN: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _get_win_by_uid_tx(self, tx, uid: str) -> Optional[dict]:
        query = "MATCH (w:WIN {uid: $uid}) RETURN w"
        result = tx.run(query, uid=uid)
        record = result.single()
        return dict(record['w']) if record and record['w'] else None

    def list_wins(self, skip: int = 0, limit: int = 25) -> List[Win]:
        """Retrieves a list of WINs with pagination."""
        logging.debug(f"WinService.list_wins: Bắt đầu lấy danh sách WINs. Skip: {skip}, Limit: {limit}")
        try:
            with self._get_db().session() as session:
                raw_results = session.read_transaction(self._list_wins_tx, skip, limit)
                logging.debug(f"WinService.list_wins: Đã nhận {len(raw_results)} kết quả thô từ Neo4j.")
                
                processed_wins = []
                for raw_win_data in raw_results:
                    # Chuyển đổi các kiểu dữ liệu Neo4j, đặc biệt là DateTime
                    converted_data = self._convert_neo4j_types(raw_win_data)
                    logging.debug(f"WinService.list_wins: Dữ liệu WIN đã chuyển đổi: {converted_data}")
                    processed_wins.append(Win(**converted_data))
                
                logging.debug(f"WinService.list_wins: Hoàn thành, trả về {len(processed_wins)} WINs.")
                return processed_wins
        except Exception as e:
            logging.error(f"WinService.list_wins: Lỗi khi lấy danh sách WINs: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return [] # Trả về danh sách rỗng trong trường hợp lỗi

    @staticmethod
    def _list_wins_tx(tx, skip: int, limit: int) -> List[dict]:
        logging.debug(f"WinService._list_wins_tx: Thực thi truy vấn lấy WINs. Skip: {skip}, Limit: {limit}")
        query = (
            "MATCH (w:WIN) "
            "RETURN w.uid AS uid, w.summary AS summary, w.description AS description, w.win_type AS win_type, "
            "w.created_at AS created_at, w.updated_at AS updated_at, w.status AS status, w.priority AS priority, "
            "w.start_date AS start_date, w.end_date AS end_date, w.target_date AS target_date, w.progress AS progress, "
            "w.owner_id AS owner_id, w.team_id AS team_id, w.tags AS tags, w.properties AS properties "
            "ORDER BY w.created_at DESC "
            "SKIP $skip LIMIT $limit"
        )
        try:
            result = tx.run(query, skip=skip, limit=limit)
            # Trả về danh sách các dict, mỗi dict là một WIN
            # Đảm bảo tất cả các trường được trả về từ truy vấn Cypher
            # Neo4j driver tự động chuyển đổi các kiểu cơ bản (string, int, float, boolean, list, dict)
            # DateTime cần được xử lý đặc biệt sau khi lấy dữ liệu
            win_list = [record.data() for record in result] # record.data() trả về dict của tất cả các trường
            logging.debug(f"WinService._list_wins_tx: Truy vấn thành công, {len(win_list)} WINs được trả về.")
            return win_list
        except Exception as e:
            logging.error(f"WinService._list_wins_tx: Lỗi trong quá trình thực thi Cypher: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return []

    def update_win(self, win_id: str, win_update: WinUpdate) -> Optional[Win]:
        """Updates an existing WIN."""
        update_data = win_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_win_by_id(win_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_win_tx, win_id, update_data)
            return Win(**result) if result else None

    @staticmethod
    def _update_win_tx(tx, win_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"w.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('w.updatedAt = $updatedAt')
            set_clauses.append('w.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (w:WIN {{winId: $winId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN w"
        )
        params = {'winId': win_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['w']) if record and record['w'] else None

    def delete_win(self, win_id: str) -> bool:
        """Deletes a WIN by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_win_tx, win_id)
            return result

    @staticmethod
    def _delete_win_tx(tx, win_id: str) -> bool:
        query = "MATCH (w:WIN {winId: $winId}) DETACH DELETE w"
        result = tx.run(query, winId=win_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
win_service = WinService()
