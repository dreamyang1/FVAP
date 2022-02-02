from losses.fair_demographic_parity_loss import fair_demographic_parity_loss
from losses.fair_equalized_odds_loss import fair_equalized_odds_loss
from losses.fair_intersection_over_union import fair_intersection_over_union_loss
from losses.fair_mutual_information_loss import fair_mutual_information_3_loss, fair_mutual_information_loss

fair_losses = {
    "DemographicParity": fair_demographic_parity_loss,
    "EqualizedOdds": fair_equalized_odds_loss,
    "IntersectionOverUnion": fair_intersection_over_union_loss,
    "MutualInformation": fair_mutual_information_loss,
    "MutualInformation3": fair_mutual_information_3_loss,
}
