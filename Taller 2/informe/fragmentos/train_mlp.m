function [net, hist] = train_mlp(Xtr, Dtr, Xva, Dva, cfg)
    % Mismo ciclo de la sección 8, con error de validación por época y parada
    % temprana cuando la validación lleva cfg.patience épocas sin mejorar.
    % Sin conjunto de validación la paciencia vigila el error de entrenamiento.
    if iscell(cfg.act_hidden)
        assert(numel(cfg.act_hidden) == numel(cfg.hidden_layers), 'act_hidden debe tener una activación por capa oculta');
    end
    rng(cfg.seed);
    net = init_mlp(cfg);
    hist.train = zeros(cfg.max_epochs, 1);  hist.val = hist.train;
    mejor = Inf;  sin_mejora = 0;  mejor_net = net;  mejor_epoca = 0;
    for epoch = 1:cfg.max_epochs
        for p = randperm(size(Xtr, 1))
            [~, cache] = forward_mlp(net, Xtr(p, :)', cfg);
            net = backward_mlp(net, cache, Xtr(p, :)', Dtr(p, :)', cfg);
        end
        hist.train(epoch) = mse_mlp(net, Xtr, Dtr, cfg);
        if ~isempty(Xva), hist.val(epoch) = mse_mlp(net, Xva, Dva, cfg); end
        if hist.train(epoch) <= cfg.target_error, break; end
        if cfg.patience > 0
            if isempty(Xva), vigilado = hist.train(epoch); else, vigilado = hist.val(epoch); end
            if vigilado < mejor
                mejor = vigilado;  sin_mejora = 0;  mejor_net = net;  mejor_epoca = epoch;
            else
                sin_mejora = sin_mejora + 1;
                if sin_mejora >= cfg.patience, break; end
            end
        end
    end
    hist.convergio = hist.train(epoch) <= cfg.target_error;
    if cfg.patience > 0 && ~hist.convergio
        net = mejor_net;
    else
        mejor_epoca = epoch;
    end
    hist.train = hist.train(1:epoch);  hist.val = hist.val(1:epoch);
    hist.epochs = epoch;  hist.best_epoch = mejor_epoca;
end
