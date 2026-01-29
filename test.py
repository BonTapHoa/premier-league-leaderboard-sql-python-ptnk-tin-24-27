from flask import Flask, jsonify, request, abort

app = Flask(__name__)

tasks = [
    {
        "id": 1,
        "title": "Học Python Flask",
        "description": "Tìm hiểu cách tạo API cơ bản",
        "done": False,
    },
    {
        "id": 2,
        "title": "Làm bài tập về nhà",
        "description": "Môn Toán và Tiếng Anh",
        "done": False,
    },
]


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks})


@app.route("/tasks", methods=["POST"])
def create_task():
    if not request.json or not "title" in request.json:
        abort(400)

    if len(tasks) == 0:
        new_id = 1
    else:
        new_id = tasks[-1]["id"] + 1

    task = {
        "id": new_id,
        "title": request.json["title"],
        "description": request.json.get("description", ""),
        "done": False,
    }

    tasks.append(task)
    return jsonify({"task": task}), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]

    if len(task) == 0:
        abort(404)

    tasks.remove(task[0])
    return jsonify({"result": True})


if __name__ == "__main__":
    app.run(debug=True)