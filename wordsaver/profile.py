# -*- coding: utf-8 -*-

import cProfile

cProfile.run(r"""
import wordsaver.dbop as dbop
dbop.getallword()
""")
