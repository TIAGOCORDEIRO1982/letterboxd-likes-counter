def create_bubble_chart(word_counts):

    # ordenar por frequência
    word_counts = sorted(word_counts, key=lambda x: x[1], reverse=True)

    words = [w for w, _ in word_counts]
    values = [v for _, v in word_counts]

    max_val = max(values)

    sizes = [60 + (v / max_val) * 120 for v in values]
    radii = [s / 2 for s in sizes]

    gap = 10  # espaço entre bolhas

    x = [0]
    y = [0]

    # distribuir em círculo ao redor
    angle_step = 2 * math.pi / max(1, len(words) - 1)

    current_radius = radii[0] + gap

    for i in range(1, len(words)):

        placed = False

        for ring in range(1, 10):

            radius_ring = current_radius + ring * (max(radii) + gap)

            for j in range(len(words)):

                angle = j * angle_step

                px = math.cos(angle) * radius_ring
                py = math.sin(angle) * radius_ring

                collision = False

                for k in range(len(x)):
                    dist = math.sqrt((px - x[k])**2 + (py - y[k])**2)

                    if dist < (radii[i] + radii[k] + gap):
                        collision = True
                        break

                if not collision:
                    x.append(px)
                    y.append(py)
                    placed = True
                    break

            if placed:
                break

        if not placed:
            x.append(px)
            y.append(py)

    labels = [f"{w}<br>{v}x" for w, v in word_counts]

    colors = [
        "#A78BFA","#60A5FA","#34D399","#FBBF24",
        "#F87171","#F472B6","#38BDF8","#818CF8",
        "#4ADE80","#FB923C","#C084FC","#22D3EE"
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+text',
        text=labels,
        textposition="middle center",
        marker=dict(
            size=sizes,
            color=colors[:len(words)]
        ),
        textfont=dict(size=13, color="white"),
        hoverinfo="text"
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        height=550,
        margin=dict(l=0, r=0, t=20, b=0)
    )

    return fig