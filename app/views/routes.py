from flask import Blueprint, render_template

view_bp = Blueprint(
    'view_bp',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)


@view_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')
