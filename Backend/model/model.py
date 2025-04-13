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
        with_background=True
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
                with_background=True
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
                        with_background=True
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
                    with_background=True
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
                        with_background=True
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
                            with_background=True
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
                            with_background=True
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
                            with_background=True
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
    

def generate_scan_pdf(assessment_results, client_id=None, scan_id=None, scan_reason="Consult", output_dir='../reports'):
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
    import sys

    os.makedirs(output_dir, exist_ok=True)

    # Determine PDF filename based on scan_id or timestamp
    if scan_id:
        pdf_filename = os.path.join(output_dir, f"client_{client_id}_scan_{scan_id}.pdf")
        print(f"Generating PDF with scan ID: {scan_id} at path: {pdf_filename}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = os.path.join(output_dir, f"client_{client_id}_scan_{timestamp}.pdf")
        print(f"Generating PDF with timestamp: {timestamp} at path: {pdf_filename}")

    client_info_added = False

    # Try to get client info if client_id is provided
    if client_id is not None:
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from domain.entities import Client
            
            # This needs to be in a Flask app context
            try:
                from flask import current_app
                try:
                    client = Client.query.get(client_id)
                    client_info_added = True
                except Exception as e:
                    print(f"Could not query client: {e}")
            except:
                print("Not in Flask context, skipping client info retrieval")
        except ImportError:
            print("Could not import Client model, skipping client info")

    # Set up document styles
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

    # Add title
    title = Paragraph("AlignAI Body Mobility Report", styles['Title'])
    elements.append(title)

    # Add client info if available
    if client_info_added and 'client' in locals():
        elements.append(Paragraph(f"Patient: {client.first_name} {client.last_name}", styles['Heading2']))
        elements.append(Paragraph(f"Age: {client.age}", styles['Normal']))
        elements.append(Paragraph(f"Gender: {client.gender}", styles['Normal']))
        elements.append(Paragraph(f"Reason for Scan: {scan_reason}", styles['Normal']))
        if client.previous_conditions:
            elements.append(Paragraph(f"Previous Conditions: {client.previous_conditions}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

    # Create the document
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Add scan date
    date_line = Paragraph(f"Scan Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
    elements.append(date_line)
    elements.append(Spacer(1, 0.2*inch))

    # Add overall score and interpretation
    overall_score = assessment_results['overall_score']
    elements.append(Paragraph(f"Overall Scan Score: {overall_score:.1f}%", styles['Heading1']))

    # Add interpretation based on score
    if overall_score >= 90:
        interpretation = "Excellent mobility. Your movement patterns are very good with minimal risk of injury."
    elif overall_score >= 80:
        interpretation = "Good mobility. Your movement patterns show good control with some minor areas for improvement."
    elif overall_score >= 70:
        interpretation = "Fair mobility. Some movement patterns could be improved to reduce risk of injury."
    elif overall_score >= 60:
        interpretation = "Below average mobility. Several movement patterns show compensation that could lead to injury if not addressed."
    else:
        interpretation = "Limited mobility. Significant movement compensations detected that should be addressed to prevent injury."

    elements.append(Paragraph(f"Interpretation: {interpretation}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Add bar chart for scores
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

    # Add detailed scores
    elements.append(Paragraph("Mobility Assessment Details", styles['Heading1']))
    
    elements.append(Paragraph(f"Balance Score: {assessment_results['balance_score']:.1f}%", styles['Heading2']))
    elements.append(Paragraph("This score measures your ability to maintain stable posture during movement.", styles['Normal']))
    
    elements.append(Paragraph(f"Stepping Score: {assessment_results['stepping_score']:.1f}%", styles['Heading2']))
    elements.append(Paragraph("This score measures your gait stability and symmetry during stepping movements.", styles['Normal']))
    
    elements.append(Paragraph(f"Squat Score: {assessment_results['squat_score']:.1f}%", styles['Heading2']))
    elements.append(Paragraph("This score evaluates your squat mechanics including depth, control, and alignment.", styles['Normal']))
    
    elements.append(Paragraph(f"Posture Score: {assessment_results['posture_score']:.1f}%", styles['Heading2']))
    elements.append(Paragraph("This score assesses your spine alignment and posture during movements.", styles['Normal']))
    
    elements.append(Spacer(1, 0.2*inch))

    # Add recommendations section
    elements.append(Paragraph("Recommendations", styles['Heading1']))

    # Generate recommendations based on scores
    recommendations = []
    if assessment_results['balance_score'] < 70:
        recommendations.append("Balance Training: Consider exercises that challenge your stability, such as single-leg stands, heel-to-toe walking, or balance board activities.")
    
    if assessment_results['stepping_score'] < 70:
        recommendations.append("Gait Training: Focus on improving your stepping pattern with controlled walking exercises, marching in place, and step-ups.")
    
    if assessment_results['squat_score'] < 70:
        recommendations.append("Squat Mechanics: Work on improving your squat form with bodyweight squats, focusing on maintaining proper alignment and depth.")
    
    if assessment_results['posture_score'] < 70:
        recommendations.append("Posture Improvement: Practice exercises that strengthen core and back muscles to improve spinal alignment.")
    
    if not recommendations:
        recommendations.append("Maintenance: Continue your current exercise program to maintain your excellent mobility patterns.")
    
    for recommendation in recommendations:
        elements.append(Paragraph(f"• {recommendation}", styles['Normal']))

    # Build the document
    doc.build(elements)

    print(f"Scan report saved to: {pdf_filename}")
    return pdf_filename

# Helper function to save scan to database
def save_scan_to_db(client_id, scan_reason, assessment_results, pdf_path):
    from domain.models import db
    from domain.entities import Scan
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create scan record first to get ID
    new_scan = Scan(
        client_id=client_id,
        scan_reason=scan_reason,
        balance_score=assessment_results["balance_score"],
        stepping_score=assessment_results["stepping_score"],
        squat_score=assessment_results["squat_score"],
        posture_score=assessment_results["posture_score"],
        overall_score=assessment_results["overall_score"]
    )
    db.session.add(new_scan)
    db.session.commit()  # Commit to get scan ID
    
    # Generate PDF with the actual scan ID
    pdf_path = generate_scan_pdf(
        assessment_results, 
        client_id=client_id, 
        scan_id=new_scan.id,  # Use actual scan ID
        scan_reason=scan_reason
    )
    
    # Update scan with PDF path
    new_scan.report_pdf = os.path.relpath(pdf_path, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db.session.commit()

    print(f"Scan saved to database with ID: {new_scan.id}")
    return new_scan

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
        # Create database record first to get the scan ID
        if client_id:
            try:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.append(parent_dir)
                
                try:
                    from app import create_app
                    from domain.models import db
                    from domain.entities import Scan
                    
                    # Create app context
                    app = create_app()
                    with app.app_context():
                        # Create scan record WITHOUT pdf_path initially
                        new_scan = Scan(
                            client_id=client_id,
                            scan_reason=scan_reason,
                            balance_score=assessment_results['balance_score'],
                            stepping_score=assessment_results['stepping_score'],
                            squat_score=assessment_results['squat_score'],
                            posture_score=assessment_results['posture_score'],
                            overall_score=assessment_results['overall_score']
                        )
                        db.session.add(new_scan)
                        db.session.commit()
                        
                        # Now generate PDF with the actual scan ID
                        scan_id = new_scan.id
                        pdf_path = generate_scan_pdf(assessment_results, client_id=client_id, 
                                                   scan_id=scan_id, scan_reason=scan_reason)
                        
                        # Update the scan record with the PDF path
                        new_scan.report_pdf = pdf_path
                        db.session.commit()
                        
                        print(f"Scan saved to database with ID: {scan_id}")
                        print(f"PDF saved to: {pdf_path}")
                except ImportError as e:
                    print(f"Error importing Flask modules: {e}")
            except Exception as e:
                print(f"Error during database operations: {e}")
                traceback.print_exc()
        else:
            # If no client_id, still generate PDF but don't save to DB
            pdf_path = generate_scan_pdf(assessment_results, scan_reason=scan_reason)
            print(f"PDF saved to: {pdf_path} (not linked to any client)")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        traceback.print_exc()

    print(json.dumps(assessment_results, indent=4))
