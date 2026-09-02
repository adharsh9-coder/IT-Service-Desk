import os
from werkzeug.utils import secure_filename
from dao.interaction_dao import InteractionDAO
from model.interactions import TicketComment, TicketAttachment, Feedback

interaction_dao = InteractionDAO()

class InteractionService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'log'}
    MAX_FILE_SIZE = 5 * 1024 * 1024 

    def add_comment(self, ticket_id, user_id, text):
        comment = TicketComment(ticket_id=ticket_id, user_id=user_id, comment_text=text)
        return interaction_dao.add_comment(comment)

    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def process_attachment(self, file_object, ticket_id, uploader_id, upload_folder):
        if not file_object or file_object.filename == '':
            # raise ValueError("No file provided.")
            return None
            
        if not self._allowed_file(file_object.filename):
            raise ValueError("Invalid file type. Only images, PDFs, and text/logs are allowed.")

        filename = secure_filename(file_object.filename)
        file_path = os.path.join(upload_folder, filename)

        file_object.save(file_path)
        
        attachment = TicketAttachment(
            ticket_id=ticket_id, 
            uploader_id=uploader_id, 
            file_name=filename, 
            file_path=file_path
        )

        interaction_dao.add_attachment(attachment)
        
        return attachment

    def submit_feedback(self, ticket_id, employee_id, rating, comments):
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")
            
        feedback = Feedback(
            ticket_id=ticket_id, 
            employee_id=employee_id, 
            rating=rating, 
            comments=comments
        )
        
        # interaction_dao.add_feedback(feedback)
        
        return interaction_dao.add_feedback(feedback)

    def get_audit_trail(self, start_date=None, end_date=None):
        return interaction_dao.get_global_audit_trail(start_date, end_date)