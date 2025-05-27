from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory store for datasets
datasets = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.html', datasets=datasets)

@app.route('/add', methods=['GET', 'POST'])
def add_dataset():
    global next_id
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        datasets.append({'id': next_id, 'name': name, 'description': description, 'location': location})
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
        return redirect(url_for('index'))

    return render_template('dataset_form.html', title='Edit Dataset', dataset=dataset, form_action=url_for('edit_dataset', dataset_id=dataset_id))

@app.route('/delete/<int:dataset_id>')
def delete_dataset(dataset_id):
    global datasets
    datasets = [ds for ds in datasets if ds['id'] != dataset_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
