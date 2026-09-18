function dy = activation_deriv(net_in, tipo)
    % Derivada de la función de activación, evaluada en net_in.
    switch tipo
        case 'sigmoid'
            f = 1 ./ (1 + exp(-net_in));
            dy = f .* (1 - f);
        case 'tanh'
            dy = 1 - tanh(net_in).^2;
        case 'relu'
            dy = double(net_in > 0);
        case 'linear'
            dy = ones(size(net_in));
        otherwise
            error('Función de activación no reconocida: %s', tipo);
    end
end
