import mediapipe as mp
import cv2
import numpy as np
import time
from enum import Enum
import json
import sys
import os
import traceback
from PIL import Image, ImageDraw, ImageFont

from balance_tracker import BalanceTracker
from step_tracker import StepTracker
from squat_tracker import SquatTracker
from helpers import calculate_spine_angle

class ExerciseState(Enum):
    WAITING = 0
    STEPPING = 1  
    SQUATTING = 2
    COMPLETED = 3


""" Helper function for modern UI text using pillow """
def add_modern_text(
        cv2_image, 
        text, position, 
        font_path=None,   
        font_size=20, 
        text_color=(255, 255, 255), 
        with_background=False
    ):

    # Use absolute path to font file
    if font_path is None:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct absolute path to font file
        font_path = os.path.join(script_dir, "..", "fonts", "Nunito-Bold.ttf")

    # Check if font file exists
    if not os.path.isfile(font_path):
        print(f"Warning: Font file not found at {font_path}, using default font")
        # Use a default font that's guaranteed to be available
        font = ImageFont.load_default()
    else:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"Error loading font: {str(e)}, using default font")
            font = ImageFont.load_default()
    
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    
    draw = ImageDraw.Draw(pil_image)
    
    font = ImageFont.truetype(font_path, font_size)
    if not font:
        font = ImageFont.load_default()
    
    # we get text dimensions
    if hasattr(font, "getbbox"):
        # for newer pillow versions (9.2.0+)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    elif hasattr(font, "getsize"):
        # for pillow versions between 9.0.0 - 9.2.0
        text_width, text_height = font.getsize(text)
    else:
        # for old pillow version
        text_width, text_height = 0, 0
    
    if with_background:
        # draw rounded rectangle background around the text (optional)
        padding = 10
        x, y = position
        draw.rectangle(
            [(x - padding, y - padding), 
             (x + text_width + padding, y + text_height + padding)],
            fill=(32, 33, 36, 180),
            outline=(70, 70, 70),
            width=1
        )
    
    # draw text
    draw.text(position, text, font=font, fill=text_color)
    
    # we convert back to openCV format
    result_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return result_image


def draw_progress_bar(image, progress, position, width=200, height=20):
    x, y = position
    # draw background
    cv2.rectangle(image, (x, y), (x + width, y + height), (70, 70, 70), -1)
    # draw progress
    progress_width = int(width * progress / 100)
    cv2.rectangle(image, (x, y), (x + progress_width, y + height), (0, 184, 212), -1)
    return image


def run_assessment():
    # initialize the trackers
    balance_tracker = BalanceTracker()
    step_tracker = StepTracker()
    squat_tracker = SquatTracker()
    
    # exercise state
    current_state = ExerciseState.WAITING
    state_start_time = time.time()
    instructions = "Get ready for stepping exercise"
    
    # assessment results dictionary
    assessment_results = {
        "balance_score": 0,
        "stepping_score": 0,
        "squat_score": 0,
        "posture_score": 0,
        "overall_score": 0
    }

    # display dimensions
    display_width = 1920
    display_height = 1080

    # font sizes
    FONT_TITLE = 34
    FONT_HEADING = 32
    FONT_SUBHEADING = 30
    FONT_TEXT = 28
    FONT_SIDEBAR = 14
    
    
    # setup mediapipe poselandmark model
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    window_name = 'AlignAI Assessment'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, display_width, display_height)

    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    
    with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
        # webcam activation
        cap = cv2.VideoCapture(0)  # use 1 for built-in webcam, 0 for usb or external
        
        start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # resize frame to fit the display
            frame = cv2.resize(frame, (display_width, display_height))
            
            current_time = time.time()
            
            # process image for pose detection
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # extract landmarks from the body
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # update trackers based on current state
                if current_state == ExerciseState.STEPPING:
                    step_detected = step_tracker.detect_step(landmarks, mp_pose, current_time)
                    balance_tracker.add_frame_data(landmarks, mp_pose)
                    
                    # check if stepping is complete
                    if step_tracker.get_step_count() >= 10:
                        current_state = ExerciseState.SQUATTING
                        state_start_time = current_time
                        instructions = "Now perform 3 squats"
                        
                elif current_state == ExerciseState.SQUATTING:
                    squat_detected = squat_tracker.detect_squat(landmarks, mp_pose, current_time)
                    balance_tracker.add_frame_data(landmarks, mp_pose)
                    
                    # check if squatting is complete
                    if squat_tracker.get_squat_count() >= 3:
                        current_state = ExerciseState.COMPLETED
                        state_start_time = current_time
                        instructions = "Assessment complete!"
                        
                        # calculate final scores
                        assessment_results["balance_score"] = balance_tracker.calculate_balance_score()
                        assessment_results["stepping_score"] = step_tracker.get_stepping_score()
                        assessment_results["squat_score"] = squat_tracker.get_squat_score()
                        

                        if squat_tracker.spine_angles:
                            # calculate spine deviation
                            spine_angles = squat_tracker.spine_angles[-90:]

                            squat_spine_angles = [angle for angle in spine_angles if 40 <= angle <= 100]

                            if squat_spine_angles:
                                avg_spine_angle = sum(squat_spine_angles) / len(squat_spine_angles)

                                if 55 <= avg_spine_angle <= 75:
                                    posture_score = 100
                                else:
                                    posture_score = max(15, 100 - min(85, abs(avg_spine_angle - 65) * 3))

                                print(f"Average Spine Angle during squats: {avg_spine_angle:.1f}, Posture Score: {posture_score:.1f}%")
                            else:    
                                posture_score = 50 
                                print("No valid squat spine angles found, using default score")  

                        else:
                            # Fallback if no spine angles recorded
                            posture_score = 50
                            print("No spine angles recorded, using default score")    


                        assessment_results["posture_score"] = posture_score
                        
                        # calculate overall score
                        assessment_results["overall_score"] = (
                            assessment_results["balance_score"] * 0.25 +
                            assessment_results["stepping_score"] * 0.25 +
                            assessment_results["squat_score"] * 0.3 +   # plus haut pour les squats
                            assessment_results["posture_score"] * 0.2
                        )
                        
                # start stepping after 5 seconds of preparation
                elif current_state == ExerciseState.WAITING and current_time - state_start_time > 5:
                    current_state = ExerciseState.STEPPING
                    state_start_time = current_time
                    instructions = "Perform 10 steps in place"
            
            # draw skeleton first from mediapipe
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,255), thickness=3, circle_radius=5),
                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=3, circle_radius=5)
                )
            
            # current scores will be displayed on the right side
            h, w = image.shape[:2]
            sidebar_width = 300  # wider sidebar
            
            # add title to sidebar with modern text
            image = add_modern_text(
                image, 
                "AlignAI", 
                (w-sidebar_width+20, 50),
                font_size=FONT_TITLE,
                text_color=(200, 200, 255),
                with_background=False
            )
            
            # add scores to sidebar
            if current_state == ExerciseState.COMPLETED:
                # show all final scores in sidebar
                y_pos = 120
                for label, value in assessment_results.items():
                    score_text = f"{label.replace('_', ' ').title()}: {value:.1f}%"
                    image = add_modern_text(
                        image,
                        score_text, 
                        (w-sidebar_width+20, y_pos), 
                        font_size=FONT_SUBHEADING,
                        text_color=(255, 255, 255),
                        with_background=False
                    )
                    y_pos += 50
            else:
                # we show live progress
                
                # add phase info
                image = add_modern_text(
                    image,
                    f"Phase: {current_state.name}", 
                    (w-sidebar_width+20, 120),
                    font_size=FONT_TEXT,
                    text_color=(255, 255, 255),
                    with_background=False
                )
                
                # add live balance score if we have enough frames
                if len(balance_tracker.hip_positions) > 10:
                    bal_score = balance_tracker.calculate_balance_score()
                    image = add_modern_text(
                        image,
                        f"Balance: {bal_score:.1f}%", 
                        (w-sidebar_width+20, 170),
                        font_size=FONT_TEXT,
                        text_color=(255, 255, 255),
                        with_background=False
                    )
                
                # add step quality if steps have been detected
                if current_state == ExerciseState.STEPPING and step_tracker.get_step_count() > 0:
                    if len(step_tracker.step_qualities) > 0:
                        step_quality = sum(step_tracker.step_qualities) / len(step_tracker.step_qualities)
                        image = add_modern_text(
                            image,
                            f"Step Quality: {step_quality:.1f}", 
                            (w-sidebar_width+20, 220),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                
                # add squat quality if squats have been detected
                if current_state == ExerciseState.SQUATTING and squat_tracker.get_squat_count() > 0:
                    if len(squat_tracker.squat_qualities) > 0:
                        squat_quality = sum(squat_tracker.squat_qualities) / len(squat_tracker.squat_qualities)
                        image = add_modern_text(
                            image,
                            f"Squat Quality: {squat_quality:.1f}", 
                            (w-sidebar_width+20, 220),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                
            # display exercise instructions with modern text
            image = add_modern_text(
                image, 
                instructions, 
                (30, 50),
                font_size=FONT_HEADING,
                text_color=(200, 200, 255)
            )
            
            # display current progress
            if current_state == ExerciseState.STEPPING:
                steps_text = f"Steps: {step_tracker.get_step_count()}/10"
                image = add_modern_text(
                    image,
                    steps_text, 
                    (30, 120),
                    font_size=FONT_SUBHEADING,
                    text_color=(255, 255, 255)
                )
                
                # add progress bar for steps
                step_progress = (step_tracker.get_step_count() / 10) * 100
                image = draw_progress_bar(image, step_progress, (30, 160), width=500, height=20)
                
            elif current_state == ExerciseState.SQUATTING:
                squats_text = f"Squats: {squat_tracker.get_squat_count()}/3"
                image = add_modern_text(
                    image,
                    squats_text, 
                    (30, 120),
                    font_size=FONT_SUBHEADING,
                    text_color=(255, 255, 255)
                )
                
                # add progress bar for squats
                squat_progress = (squat_tracker.get_squat_count() / 3) * 100
                image = draw_progress_bar(image, squat_progress, (30, 160), width=500, height=20)
                
            elif current_state == ExerciseState.COMPLETED:
                time_in_completed = current_time - state_start_time
                if time_in_completed < 1.0:
                    completion_overlay = image.copy()
                    cv2.circle(completion_overlay, (w//2, 120), 80, (76, 175, 80), -1)
                    cv2.addWeighted(completion_overlay, 0.3, image, 0.7, 0, image)
                    
                    image = add_modern_text(
                        image,
                        "ASSESSMENT COMPLETE", 
                        (w//2 - 220, 130),
                        font_size=FONT_TEXT,
                        text_color=(76, 175, 80)
                    )
                
                # show overall score
                score_text = f"Overall Score: {assessment_results['overall_score']:.1f}%"
                image = add_modern_text(
                    image,
                    score_text, 
                    (30, 120),
                    font_size=FONT_TEXT,
                    text_color=(76, 175, 80)
                )
                
                # add individual scores
                y_position = 180
                for key, value in assessment_results.items():
                    if key != "overall_score":
                        metric_text = f"{key.replace('_', ' ').title()}: {value:.1f}%"
                        image = add_modern_text(
                            image,
                            metric_text, 
                            (50, y_position),
                            font_size=FONT_TEXT,
                            text_color=(255, 255, 255),
                            with_background=False
                        )
                        y_position += 50
            
            # display the image
            cv2.imshow(window_name, image)
            
            # check for exit ('q' for exiting the application)
            if cv2.waitKey(10) & 0xFF == ord('q') or (current_state == ExerciseState.COMPLETED and current_time - state_start_time > 5):
                break
                
        # clean up the opencv resources
        cap.release()
        cv2.destroyAllWindows()

        # ajout du pdf
        if current_state == ExerciseState.COMPLETED:
            print("Scan completed, generating PDF...")
            try:
                pdf_path = generate_scan_pdf(assessment_results)
                assessment_results['report_pdf'] = pdf_path
                print(f"Scan report saved to: {pdf_path} ")
            except Exception as e:
                print(f"Error generating PDF report: {str(e)}")
        
        return assessment_results
    

def generate_scan_pdf(assessment_results, client_id=None, scan_reason="Consult", output_dir = '../reports'):
    """ Generates a pdf report with the assessment results """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from datetime import datetime
    import os

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    client_info_added = False


    styles = getSampleStyleSheet()


    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].fontSize = 24
    styles['Title'].alignment = 1
    styles['Title'].spaceAfter = 20
    
    styles['Heading1'].fontName = 'Helvetica-Bold'
    styles['Heading1'].fontSize = 18
    styles['Heading1'].spaceAfter = 10
    
    styles['Heading2'].fontName = 'Helvetica-Bold'
    styles['Heading2'].fontSize = 14
    styles['Heading2'].spaceAfter = 8
    
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 12
    styles['Normal'].spaceAfter = 6


    elements = []

    title = Paragraph("AlignAI Body Mobility Report", styles['Title'])
    elements.append(title)

    if client_id is not None:
        try:
            client_id = int(client_id)
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            try:
                # import des client services
                from app.services.client_services import ClientService
                from app import create_app

                # Create a Flask app context
                print(f"Creating app context for client ID: {client_id}")
                app = create_app()
                with app.app_context():
                    client = ClientService.get_client_by_id(client_id)
                    if client:
                        print(f"Found client: {client.first_name} {client.last_name}")

                        client_info = [
                            ["Patient:", f"{client.first_name} {client.last_name}"],
                            ["Age:", f"{client.age}"],
                            ["Gender:", f"{client.gender}"],
                            ["Reason:", f"{scan_reason}"],
                            ["Medical History:", f"{client.previous_conditions or 'None'}"]
                        ]
                        
                        client_table = Table(client_info, colWidths=[100, 400])
                        client_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                            ('PADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                        ]))
                        
                        elements.append(client_table)
                        elements.append(Spacer(1, 0.2*inch))
                        client_info_added = True

                        pdf_filename = f"{output_dir}/client_{client_id}_scan_{timestamp}.pdf"

                    else:
                        print(f"Client with ID {client_id} not found")
                        pdf_filename = f"{output_dir}/alignai_scan_{timestamp}.pdf"

            except ImportError as e:
                print(f"Import error: {e}")
                print("Warning: Could not import Flask app modules. Client info will not be included in the report.")    
                pdf_filename = f"{output_dir}/alignai_scan_{timestamp}.pdf"
        except Exception as e:
            print(f"Warning: Invalid client ID {client_id}. Cannot convert to integer. {str(e)}")
            pdf_filename = f"{output_dir}/alignai_scan_{timestamp}.pdf"
    else:
        pdf_filename = f"{output_dir}/alignai_scan_{timestamp}.pdf"

    doc = SimpleDocTemplate(pdf_filename, page_size=letter)

    date_line = Paragraph(f"Scan Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
    elements.append(date_line)
    elements.append(Spacer(1, 0.2*inch))

    overall_score = assessment_results['overall_score']
    elements.append(Paragraph(f"Overall Scan Score : {overall_score:.1f}%", styles['Heading1']))

    # interpretation
    if overall_score >= 90:
        interpretation = "Excellent movement quality and control."
    elif overall_score >= 80:
        interpretation = "Very good movement patterns with minor improvements possible."
    elif overall_score >= 70:
        interpretation = "Good movement with specific areas for improvement."
    elif overall_score >= 60:
        interpretation = "Moderate movement quality with clear opportunities for enhancement."
    else:
        interpretation = "Significant movement pattern deficiencies requiring attention."

    elements.append(Paragraph(f"Interpretation: {interpretation}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # creation d'une chart bar pour les scores
    drawing = Drawing(400, 200)
    data = [[
        assessment_results['balance_score'],
        assessment_results['stepping_score'],
        assessment_results['squat_score'],
        assessment_results['posture_score']
    ]]

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 125
    chart.width = 300
    chart.data = data
    chart.strokeColor = colors.black
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 10
    chart.categoryAxis.labels.boxAnchor = 'ne'
    chart.categoryAxis.labels.dx = 8
    chart.categoryAxis.labels.dy = -2
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.categoryNames = ['Balance', 'Stepping', 'Squat', 'Posture']
    chart.bars[(0, 0)].fillColor = colors.lightblue
    chart.bars[(0, 1)].fillColor = colors.green
    chart.bars[(0, 2)].fillColor = colors.orange
    chart.bars[(0, 3)].fillColor = colors.lavender

    drawing.add(chart)
    elements.append(drawing)
    elements.append(Spacer(1, 0.2*inch))

    # sections des scores individuels
    elements.append(Paragraph("Balance Scan", styles['Heading2']))
    elements.append(Paragraph(f"Score: {assessment_results['balance_score']:.1f}%", styles['Normal']))
    elements.append(Paragraph("The balance score measures stability during both static and dynamic movements. ", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Stepping Score
    elements.append(Paragraph("Stepping Scan", styles['Heading2']))
    elements.append(Paragraph(f"Score: {assessment_results['stepping_score']:.1f}%", styles['Normal']))
    elements.append(Paragraph("The stepping score evaluates coordination, rhythm, and control during stepping motions. ", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Squat Score
    elements.append(Paragraph("Squat Scan", styles['Heading2']))
    elements.append(Paragraph(f"Score: {assessment_results['squat_score']:.1f}%", styles['Normal']))
    elements.append(Paragraph("The squat score analyzes hip and knee mobility, core stability, and lower body strength. ", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Posture Score
    elements.append(Paragraph("Posture Scan", styles['Heading2']))
    elements.append(Paragraph(f"Score: {assessment_results['posture_score']:.1f}%", styles['Normal']))
    elements.append(Paragraph("The posture score evaluates spine alignment and overall body position. ", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("Recommendations", styles['Heading1']))


    # recommandations basé sur les scores
    recommendations = []
    if assessment_results['balance_score'] < 70:
        recommendations.append("Focus on balance exercises such as single-leg stands and stability training.")
    
    if assessment_results['stepping_score'] < 70:
        recommendations.append("Practice stepping patterns with attention to rhythm and control.")
    
    if assessment_results['squat_score'] < 70:
        recommendations.append("Work on squat technique with emphasis on proper form and alignment.")
    
    if assessment_results['posture_score'] < 70:
        recommendations.append("Incorporate posture exercises and awareness throughout the day.")
    
    if not recommendations:
        recommendations.append("Maintain current exercise program and continue monitoring movement quality.")
    
    for recommendation in recommendations:
        elements.append(Paragraph(f"• {recommendation}", styles['Normal']))

    # on cree le document 
    doc.build(elements)

    print(f"Scan report saved to : {pdf_filename}")
    return pdf_filename

# Helper function to save scan to database
def save_scan_to_db(client_id, scan_reason, assessment_results, pdf_path):
    from domain.models import db
    from domain.entities import Scan
    
    print(f"Saving scan to database for client {client_id}...")
    # Create new scan record
    new_scan = Scan(
        client_id=client_id,
        scan_reason=scan_reason,
        balance_score=assessment_results['balance_score'],
        stepping_score=assessment_results['stepping_score'],
        squat_score=assessment_results['squat_score'],
        posture_score=assessment_results['posture_score'],
        overall_score=assessment_results['overall_score'],
        report_pdf=pdf_path
    )
    
    # Add to database
    db.session.add(new_scan)
    db.session.commit()
    print(f"Scan saved to database with ID: {new_scan.id}")
    assessment_results['scan_id'] = new_scan.id

if __name__ == "__main__":
    import sys
    import json
    import os
    import time
    import cv2
    import mediapipe as mp
    import numpy as np
    import traceback
    from datetime import datetime
    
    # Default values
    client_id = None
    scan_reason = "Consult"
    
    # Process command line arguments
    if len(sys.argv) > 1:
        try:
            print(f"Received argument: {sys.argv[1]}")
            args = json.loads(sys.argv[1])

            if 'client_id' in args:
                client_id = int(args.get('client_id'))
            else:
                client_id = None

            scan_reason = args.get('scan_reason', scan_reason)
            print(f"Running assessment for client ID: {client_id}")
            print(f"Scan reason: {scan_reason}")
        except Exception as e:
            print(f"Error parsing arguments for launching the scan: {str(e)}")

    assessment_results = run_assessment()

    try:
        print("Scan completed, generating PDF...")
        pdf_path = generate_scan_pdf(assessment_results, client_id=client_id, scan_reason=scan_reason)
        assessment_results['report_pdf'] = pdf_path
        print(f"Scan report saved to: {pdf_path}")

        # Only attempt database operations if client_id is provided
        if client_id:
            try:
                # Add parent directory to path to find app module
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.append(parent_dir)
                
                try:
                    # Use existing Flask app context if already in one
                    from flask import current_app
                    
                    # Try to get current app context
                    try:
                        # If we're already within a Flask app context, use it
                        with current_app.app_context():
                            from domain.models import db
                            from domain.entities import Scan
                            
                            print(f"Using existing Flask app context")
                            save_scan_to_db(client_id, scan_reason, assessment_results, pdf_path)
                    except RuntimeError:
                        # No current app context, create a new one
                        from app import create_app
                        from domain.models import db
                        from domain.entities import Scan
                        
                        print(f"Creating new Flask app context")
                        app = create_app()
                        with app.app_context():
                            save_scan_to_db(client_id, scan_reason, assessment_results, pdf_path)
                except ImportError as e:
                    print(f"Warning: Flask app modules not available: {str(e)}")
                    print("Skipping database save.")
            except Exception as e:
                print(f"Error during database operations: {str(e)}")
                traceback.print_exc()
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")
        traceback.print_exc()
        
    print(json.dumps(assessment_results, indent=4))
