function [W, b, mse_hist] = train_adaline(X, D, cfgA)
    [W, b] = init_adaline(cfgA);
    mse_hist = zeros(cfgA.max_epochs, 1);

    for epoch = 1:cfgA.max_epochs
        epoch_error = 0;
        for p = 1:size(X, 1)
            x = X(p, :);
            d = D(p);

            net = W * x' + b;   % salida LINEAL (sin escalón)
            y = net;

            delta = cfgA.alpha * (d - y) * x;
            W = W + delta;
            b = b + cfgA.alpha * (d - y);

            epoch_error = epoch_error + 0.5 * (d - y)^2;
        end

        mse_hist(epoch) = epoch_error / size(X, 1);
        if mse_hist(epoch) <= cfgA.target_mse
            mse_hist = mse_hist(1:epoch);
            break;
        end
    end
end
