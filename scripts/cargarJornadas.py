# -⁻- coding: UTF-8 -*-

with open('../datos/calendario.html') as f:
	local = None
	visitante = None
	partido = 1
	jornada = 1

	print 'Jornada %s' % jornada
	print '*' * 10
	for line in f:
		if jornada <= 19:
			if 'local' in line:
				partial_local = line[:line.rfind('</span>')]
				local = partial_local[partial_local.rfind('>') + 1:]
			elif 'visitante' in line:
				partial_visitante = line[:line.rfind('</span>')]
				visitante = partial_visitante[partial_visitante.rfind('>') + 1:]
			if local != None and visitante != None:
				print '%s - %s' % (local, visitante)
				local, visitante = None, None
				if partido >= 10:
					jornada += 1
					partido = 1
					print 
					print
					print 'Jornada %s' % jornada
					print '*' * 10
				else:
					partido += 1