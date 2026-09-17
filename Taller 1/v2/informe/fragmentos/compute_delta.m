function delta = compute_delta(cfg, d, y, x)
    % Calcula el incremento de pesos Delta_W segun la regla seleccionada
    % en cfg.learning_rule. `x` es un patron (vector fila), `d` la
    % salida deseada y `y` la salida actual del Perceptron (ya
    % escalonada).
    switch cfg.learning_rule
        case 'hebb'
            delta = d * x;
        case 'perceptron'
            delta = (d - y) * x;
        case 'perceptron_alpha'
            delta = cfg.alpha * (d - y) * x;
        otherwise
            error('Regla de aprendizaje no reconocida: %s', cfg.learning_rule);
    end
end
