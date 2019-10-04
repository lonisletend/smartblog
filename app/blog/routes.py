from flask import render_template, jsonify
from app.blog import bp

@bp.route('/testbp')
def testbp():
    return jsonify({
        'test': 123,
        'hahaha': '666'
    })