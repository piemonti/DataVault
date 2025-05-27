from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# In-memory store for datasets
datasets = []
next_id = 1

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', datasets=datasets)

@app.route('/dataset/<int:dataset_id>')
def dataset_detail(dataset_id):
    dataset = next((ds for ds in datasets if ds['id'] == dataset_id), None)
    if not dataset:
        return "Dataset not found", 404

    return render_template('dataset_detail.html', dataset=dataset)

@app.route('/add', methods=['GET', 'POST'])
def add_dataset():
    global next_id
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_path = unique_filename

        datasets.append({
            'id': next_id,
            'name': name,
            'description': description,
            'location': location,
            'image_path': image_path
        })
        next_id += 1
        return redirect(url_for('index'))
    return render_template('dataset_form.html', title='Add Dataset', form_action=url_for('add_dataset'))

@app.route('/edit/<int:dataset_id>', methods=['GET', 'POST'])
def edit_dataset(dataset_id):
    dataset = next((ds for ds in datasets if ds['id'] == dataset_id), None)
    if not dataset:
        return "Dataset not found", 404

    if request.method == 'POST':
        dataset['name'] = request.form['name']
        dataset['description'] = request.form['description']
        dataset['location'] = request.form['location']

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Remove old image if exists
                if dataset.get('image_path') and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], dataset['image_path'])):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], dataset['image_path']))
                    except:
                        pass  # If removal fails, continue anyway

                # Save new image
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                dataset['image_path'] = unique_filename

        return redirect(url_for('index'))

    return render_template('dataset_form.html', title='Edit Dataset', dataset=dataset, form_action=url_for('edit_dataset', dataset_id=dataset_id))

@app.route('/delete/<int:dataset_id>')
def delete_dataset(dataset_id):
    global datasets
    dataset = next((ds for ds in datasets if ds['id'] == dataset_id), None)

    # Remove associated image if it exists
    if dataset and dataset.get('image_path'):
        try:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], dataset['image_path'])
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass  # If removal fails, continue anyway

    datasets = [ds for ds in datasets if ds['id'] != dataset_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
